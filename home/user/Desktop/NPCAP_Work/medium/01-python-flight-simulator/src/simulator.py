#!/usr/bin/env python3
"""
Flight Simulator - асинхронный симулятор полёта БПЛА.

Задание: реализуйте логику движения между waypoints
и отправку MAVLink телеметрии.
"""

import argparse
import asyncio
import json
import math
import struct
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Waypoint:
    """Точка маршрута."""
    lat: float
    lon: float
    alt: float
    speed: float = 10.0


@dataclass
class DroneState:
    """Состояние дрона."""
    lat: float = 55.7558
    lon: float = 37.6173
    alt: float = 0.0
    
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
    
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    heading: int = 0
    
    groundspeed: float = 0.0
    airspeed: float = 0.0
    
    battery: float = 100.0
    battery_voltage: float = 12.6
    
    armed: bool = False
    mode: str = "STABILIZE"
    
    home_lat: float = 55.7558
    home_lon: float = 37.6173


class MAVLinkSender:
    """Отправщик MAVLink сообщений."""
    
    MAGIC = 0xFE
    
    def __init__(self, system_id: int = 1, component_id: int = 1):
        self.system_id = system_id
        self.component_id = component_id
        self.sequence = 0
    
    @staticmethod
    def crc_accumulate(byte: int, crc: int) -> int:
        tmp = byte ^ (crc & 0xFF)
        tmp ^= (tmp << 4) & 0xFF
        return ((crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)) & 0xFFFF
    
    def _pack(self, msg_id: int, payload: bytes, crc_extra: int) -> bytes:
        """Упаковать MAVLink v1 пакет."""
        header = struct.pack('<BBBBBB',
            self.MAGIC, len(payload), self.sequence,
            self.system_id, self.component_id, msg_id
        )
        self.sequence = (self.sequence + 1) & 0xFF
        
        crc = 0xFFFF
        for b in header[1:] + payload:
            crc = self.crc_accumulate(b, crc)
        crc = self.crc_accumulate(crc_extra, crc)
        
        return header + payload + struct.pack('<H', crc)
    
    def heartbeat(self, state: DroneState) -> bytes:
        """HEARTBEAT сообщение."""
        mode_map = {"STABILIZE": 80, "GUIDED": 88, "AUTO": 92, "LAND": 93, "RTL": 94}
        custom_mode = mode_map.get(state.mode, 80)
        base_mode = 0x80 | (0x10 if state.armed else 0)
        
        payload = struct.pack('<IBBBBB',
            custom_mode, 2, 3, base_mode, 4 if state.armed else 3, 3
        )
        return self._pack(0, payload, 50)
    
    def global_position_int(self, state: DroneState) -> bytes:
        """GLOBAL_POSITION_INT сообщение."""
        time_ms = int(time.time() * 1000) & 0xFFFFFFFF
        payload = struct.pack('<IiiiihhhH',
            time_ms,
            int(state.lat * 1e7), int(state.lon * 1e7),
            int(state.alt * 1000), int(state.alt * 1000),
            int(state.vx * 100), int(state.vy * 100), int(state.vz * 100),
            state.heading * 100
        )
        return self._pack(33, payload, 104)
    
    def vfr_hud(self, state: DroneState) -> bytes:
        """VFR_HUD сообщение."""
        payload = struct.pack('<ffffhH',
            state.airspeed, state.groundspeed, state.alt, state.vz, state.heading, 50
        )
        return self._pack(74, payload, 20)


class FlightSimulator:
    """Асинхронный симулятор полёта."""
    
    # Физические параметры
    MAX_SPEED = 15.0  # м/с
    ACCELERATION = 2.0  # м/с²
    CLIMB_RATE = 3.0  # м/с
    WP_RADIUS = 5.0  # м
    
    def __init__(self, system_id: int = 1):
        self.state = DroneState()
        self.mission: list[Waypoint] = []
        self.current_wp: int = 0
        self.mission_active: bool = False
        self.paused: bool = False
        self.running: bool = False
        
        self.mavlink = MAVLinkSender(system_id=system_id)
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.telemetry_addr: tuple = ('127.0.0.1', 14551)
    
    async def load_mission(self, filepath: str) -> bool:
        """
        Загрузить миссию из JSON файла.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if 'home' in data:
                self.state.home_lat = data['home']['lat']
                self.state.home_lon = data['home']['lon']
                self.state.lat = data['home']['lat']
                self.state.lon = data['home']['lon']
                self.state.alt = data['home']['alt']

                self.mission = []
                for wp in data['waypoints']:
                    waypoint = Waypoint(
                        lat=wp['lat'],
                        lon=wp['lon'],
                        alt=wp['alt'],
                        speed=wp['speed']
                    )
                    self.mission.append(waypoint)
                
                self.current_wp = 0
                print(f"Mission loaded: {len(self.mission)} waypoints")
                return True
        
        except Exception as e:
            return False
    
    def arm(self) -> bool:
        """
        Армировать дрон.
        """
        if self.state.armed:
            print("Drone already armed")
            return False
        
        self.state.armed = True
        self.state.mode = "GUIDED"
        print("Drone armed")
        return True
    
    def disarm(self) -> bool:
        """
        Дизармировать дрон.
        
        TODO: Реализуйте дизармирование
        """
        if not self.state.armed:
            print("Drone already disarmed")
            return False
        
        # Проверка: нельзя дизармить в воздухе
        if self.state.alt > 1.0:
            print("Cannot disarm: drone is in air")
            return False
        
        self.state.armed = False  # ✅ Правильно
        self.state.mode = "STABILIZE"  # ✅ Правильный режим
        self.state.vx = 0  # Останавливаем движение
        self.state.vy = 0
        self.state.vz = 0
        print("Drone disarmed")
        return True
    
    def start_mission(self) -> bool:
        """
        Начать выполнение миссии.
        """
        if not self.state.armed:
            print("Cannot start mission: drone not armed")
            return False
        
        if not self.mission:
            print("Cannot start mission: no mission loaded")
            return False
        
        if self.mission_active:
            print("Mission already active")
            return False
        
        self.mission_active = True
        self.state.mode = "AUTO"
        print("Mission started")
        return True
    
    def pause_mission(self):
        """Приостановить миссию."""
        if self.mission_active:
            self.paused = True
            self.state.mode = "GUIDED"
    
    def resume_mission(self):
        """Возобновить миссию."""
        if self.paused:
            self.paused = False
            self.state.mode = "AUTO"
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Расстояние между точками в метрах."""
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    @staticmethod
    def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Азимут от точки 1 к точке 2 в радианах."""
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dlam = math.radians(lon2 - lon1)
        
        y = math.sin(dlam) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
        return math.atan2(y, x)
    
    def update_physics(self, dt: float):
        """
        Обновить физику движения.
        
        TODO: Реализуйте физику движения
        
        Шаги:
        1. Если не армирован или миссия не активна - выход
        2. Получить текущий waypoint
        3. Вычислить расстояние и направление
        4. Если расстояние < WP_RADIUS - перейти к следующему
        5. Вычислить желаемую скорость (с учётом ускорения)
        6. Обновить позицию: lat += dlat, lon += dlon
        7. Обновить высоту (с учётом CLIMB_RATE)
        8. Обновить heading, groundspeed
        9. Разряд батареи: battery -= 0.1 * dt
        """
        if not self.state.armed:
            return
        
        if not self.mission_active or self.paused:
            return
        
        # Проверка на оставшиеся точки
        if self.current_wp >= len(self.mission):
            self.mission_active = False
            return
        
        # Загрузка координат точки
        target = self.mission[self.current_wp]
        
        # Расчет расстояния по формуле Хаверсина
        distance = self.haversine_distance(
            self.state.lat, self.state.lon,
            target.lat, target.lon
        )

        # Расчет расстояния с высотой упрощенной формулой при помощи формулы Пифагора
        distance = math.sqrt(distance**2 + (self.state.alt - target.alt)**2)
        
        # Проверка на расстояние до радиуса точки
        if distance < self.WP_RADIUS:
            self.current_wp += 1
            print(f"Waypoint {self.current_wp} reached")
            return
        
        # Расчет направления дрона
        bearing_rad = self.bearing(
            self.state.lat, self.state.lon,
            target.lat, target.lon
        )
        
        # Желательная скорость
        desired_speed = target.speed
        
        # Желательная скорость по координатам x и y
        desired_speed_x = desired_speed * math.sin(bearing_rad)   # восток-запад
        desired_speed_y = desired_speed * math.cos(bearing_rad)   # север-юг
        
        # Расчет разницы между желательной скоростью и текущей скоростью дрона
        delta_vx = desired_speed_x - self.state.vx
        delta_vy = desired_speed_y - self.state.vy
        max_delta = self.ACCELERATION * dt

        # Расчитывание ускорения для дрона
        # Если разница между желательной и текущей скоростью
        # ниже максимального ускорения, то ускорение будет равно
        # разнице между желательной и текущей скоростью
        if delta_vx > max_delta:
            delta_vx = max_delta
        elif delta_vx < -max_delta:
            delta_vx = -max_delta

        if delta_vy > max_delta:
            delta_vy = max_delta
        elif delta_vy < -max_delta:
            delta_vy = -max_delta

        # Изменение скорости по x и y
        self.state.vx += delta_vx
        self.state.vy += delta_vy

        # Расчет разницы между высотой дрона и точки
        alt_diff = target.alt - self.state.alt
        max_vertical_change = self.CLIMB_RATE * dt

        # Расчет изменения вертикальной скорости и направления
        if abs(alt_diff) > max_vertical_change:
            if alt_diff > 0:
                self.state.vz = self.CLIMB_RATE  
            else:
                self.state.vz = -self.CLIMB_RATE  
        else:
            if dt > 0:
                self.state.vz = alt_diff / dt
            else:
                self.state.vz = 0
        
        # Конвертация координат в долготу и широту
        earth_radius = 6371000  # метры
        lat_change = (self.state.vy * dt) / earth_radius
        lon_change = (self.state.vx * dt) / (earth_radius * math.cos(math.radians(self.state.lat)))
        
        self.state.lat += math.degrees(lat_change)
        self.state.lon += math.degrees(lon_change)
        self.state.alt += self.state.vz * dt
        
        # Обновление скорости относительно земли и направления движения
        self.state.groundspeed = math.sqrt(self.state.vx**2 + self.state.vy**2)
        self.state.heading = int(math.degrees(bearing_rad)) % 360
        
        # Разряд батареи
        self.state.battery -= 0.1 * dt
        self.state.battery = max(0, self.state.battery)
        pass
    
    async def telemetry_loop(self):
        """Цикл отправки телеметрии."""
        while self.running:
            if self.transport:
                messages = [
                    self.mavlink.heartbeat(self.state),
                    self.mavlink.global_position_int(self.state),
                    self.mavlink.vfr_hud(self.state),
                ]
                for msg in messages:
                    self.transport.sendto(msg, self.telemetry_addr)
            
            await asyncio.sleep(0.1)  # 10 Hz
    
    async def physics_loop(self):
        """Цикл обновления физики."""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            self.update_physics(dt)
            
            await asyncio.sleep(0.05)  # 20 Hz
    
    async def command_handler(self, data: bytes, addr: tuple):
        """Обработчик входящих команд."""
        try:
            cmd = json.loads(data.decode())
            command = cmd.get('command', '')
            
            if command == 'arm':
                success = self.arm()
                print(f"ARM: {'OK' if success else 'FAILED'}")
            elif command == 'disarm':
                success = self.disarm()
                print(f"DISARM: {'OK' if success else 'FAILED'}")
            elif command == 'start':
                success = self.start_mission()
                print(f"START: {'OK' if success else 'FAILED'}")
            elif command == 'pause':
                self.pause_mission()
                print("PAUSED")
            elif command == 'resume':
                self.resume_mission()
                print("RESUMED")
            else:
                print(f"Unknown command: {command}")
        except Exception as e:
            print(f"Command error: {e}")
    
    async def run(self, telemetry_port: int = 14550, command_port: int = 14551):
        """Запустить симулятор."""
        self.running = True
        self.telemetry_addr = ('127.0.0.1', telemetry_port)
        
        # Создаём UDP сокет для телеметрии
        loop = asyncio.get_event_loop()
        
        class TelemetryProtocol(asyncio.DatagramProtocol):
            def __init__(self, simulator):
                self.simulator = simulator
            
            def connection_made(self, transport):
                self.simulator.transport = transport
        
        transport, _ = await loop.create_datagram_endpoint(
            lambda: TelemetryProtocol(self),
            local_addr=('0.0.0.0', 0)
        )
        
        # Создаём UDP сокет для команд
        class CommandProtocol(asyncio.DatagramProtocol):
            def __init__(self, simulator):
                self.simulator = simulator
            
            def datagram_received(self, data, addr):
                asyncio.create_task(self.simulator.command_handler(data, addr))
        
        await loop.create_datagram_endpoint(
            lambda: CommandProtocol(self),
            local_addr=('0.0.0.0', command_port)
        )
        
        print(f"Flight Simulator started")
        print(f"Telemetry -> {self.telemetry_addr}")
        print(f"Commands <- 0.0.0.0:{command_port}")
        
        # Запускаем основные циклы
        try:
            await asyncio.gather(
                self.telemetry_loop(),
                self.physics_loop(),
            )
        except asyncio.CancelledError:
            pass
        finally:
            self.running = False
            transport.close()


async def main():
    parser = argparse.ArgumentParser(description='Flight Simulator')
    parser.add_argument('--mission', type=str, help='Mission JSON file')
    parser.add_argument('--telemetry-port', type=int, default=14550)
    parser.add_argument('--command-port', type=int, default=14551)
    parser.add_argument('--system-id', type=int, default=1)
    
    args = parser.parse_args()
    
    simulator = FlightSimulator(system_id=args.system_id)
    
    if args.mission:
        success = await simulator.load_mission(args.mission)
        if success:
            print(f"Mission loaded: {len(simulator.mission)} waypoints")
        else:
            print("Failed to load mission")
    
    try:
        await simulator.run(args.telemetry_port, args.command_port)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == '__main__':
    asyncio.run(main())
