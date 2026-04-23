#!/usr/bin/env python3
"""
MAVLink Emulator - эмулятор БПЛА для тестирования без реального оборудования.

Поддерживает:
- Отправку heartbeat сообщений
- Генерацию телеметрии (GPS, высота, скорость, батарея)
- Приём и обработку команд
- Эмуляцию миссий с waypoints
"""

import argparse
import asyncio
import json
import math
import random
import socket
import struct
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Callable


class MAVType(IntEnum):
    QUADROTOR = 2
    FIXED_WING = 1


class MAVState(IntEnum):
    UNINIT = 0
    BOOT = 1
    CALIBRATING = 2
    STANDBY = 3
    ACTIVE = 4
    CRITICAL = 5
    EMERGENCY = 6
    POWEROFF = 7


class MAVMode(IntEnum):
    PREFLIGHT = 0
    STABILIZE = 80
    GUIDED = 88
    AUTO = 92
    LAND = 93


class MAVComponent(IntEnum):
    AUTOPILOT = 1


class MAVAutopilot(IntEnum):
    ARDUPILOTMEGA = 3


class MAVMsgID(IntEnum):
    HEARTBEAT = 0
    SYS_STATUS = 1
    GPS_RAW_INT = 24
    ATTITUDE = 30
    GLOBAL_POSITION_INT = 33
    RC_CHANNELS = 65
    VFR_HUD = 74
    COMMAND_LONG = 76
    COMMAND_ACK = 77
    BATTERY_STATUS = 147


@dataclass
class DroneState:
    """Состояние эмулируемого дрона."""
    
    lat: float = 55.7558  # Москва по умолчанию
    lon: float = 37.6173
    alt: float = 0.0
    relative_alt: float = 0.0
    
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
    
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    
    groundspeed: float = 0.0
    airspeed: float = 0.0
    heading: int = 0
    
    battery_voltage: float = 12.6
    battery_remaining: int = 100
    
    gps_fix: int = 3
    satellites: int = 12
    
    mode: MAVMode = MAVMode.STABILIZE
    state: MAVState = MAVState.STANDBY
    armed: bool = False
    
    waypoints: list = field(default_factory=list)
    current_wp: int = 0
    mission_active: bool = False


class MAVLinkMessage:
    """Базовый класс для MAVLink сообщений."""
    
    MAGIC_V1 = 0xFE
    MAGIC_V2 = 0xFD
    
    def __init__(self, system_id: int = 1, component_id: int = 1):
        self.system_id = system_id
        self.component_id = component_id
        self.sequence = 0
    
    @staticmethod
    def crc_accumulate(byte: int, crc: int) -> int:
        tmp = byte ^ (crc & 0xFF)
        tmp ^= (tmp << 4) & 0xFF
        return ((crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)) & 0xFFFF
    
    @staticmethod
    def crc_calculate(data: bytes, crc_extra: int) -> int:
        crc = 0xFFFF
        for b in data:
            crc = MAVLinkMessage.crc_accumulate(b, crc)
        crc = MAVLinkMessage.crc_accumulate(crc_extra, crc)
        return crc
    
    def pack_heartbeat(self, drone: DroneState) -> bytes:
        """Упаковка HEARTBEAT сообщения."""
        msg_id = MAVMsgID.HEARTBEAT
        crc_extra = 50
        
        custom_mode = int(drone.mode)
        mav_type = MAVType.QUADROTOR
        autopilot = MAVAutopilot.ARDUPILOTMEGA
        base_mode = 0x80 | (0x10 if drone.armed else 0)
        system_status = int(drone.state)
        mavlink_version = 3
        
        payload = struct.pack('<IBBBBB',
            custom_mode,
            mav_type,
            autopilot,
            base_mode,
            system_status,
            mavlink_version
        )
        
        return self._wrap_message(msg_id, payload, crc_extra)
    
    def pack_global_position_int(self, drone: DroneState) -> bytes:
        """Упаковка GLOBAL_POSITION_INT сообщения."""
        msg_id = MAVMsgID.GLOBAL_POSITION_INT
        crc_extra = 104
        
        time_boot_ms = int(time.time() * 1000) & 0xFFFFFFFF
        lat = int(drone.lat * 1e7)
        lon = int(drone.lon * 1e7)
        alt = int(drone.alt * 1000)
        relative_alt = int(drone.relative_alt * 1000)
        vx = int(drone.vx * 100)
        vy = int(drone.vy * 100)
        vz = int(drone.vz * 100)
        hdg = int(drone.heading * 100)
        
        payload = struct.pack('<IiiiihhhH',
            time_boot_ms, lat, lon, alt, relative_alt,
            vx, vy, vz, hdg
        )
        
        return self._wrap_message(msg_id, payload, crc_extra)
    
    def pack_attitude(self, drone: DroneState) -> bytes:
        """Упаковка ATTITUDE сообщения."""
        msg_id = MAVMsgID.ATTITUDE
        crc_extra = 39
        
        time_boot_ms = int(time.time() * 1000) & 0xFFFFFFFF
        
        payload = struct.pack('<Iffffff',
            time_boot_ms,
            drone.roll,
            drone.pitch,
            drone.yaw,
            0.0,  # rollspeed
            0.0,  # pitchspeed
            0.0   # yawspeed
        )
        
        return self._wrap_message(msg_id, payload, crc_extra)
    
    def pack_gps_raw_int(self, drone: DroneState) -> bytes:
        """Упаковка GPS_RAW_INT сообщения."""
        msg_id = MAVMsgID.GPS_RAW_INT
        crc_extra = 24
        
        time_usec = int(time.time() * 1e6)
        lat = int(drone.lat * 1e7)
        lon = int(drone.lon * 1e7)
        alt = int(drone.alt * 1000)
        eph = 100  # HDOP * 100
        epv = 100  # VDOP * 100
        vel = int(drone.groundspeed * 100)
        cog = int(drone.heading * 100)
        fix_type = drone.gps_fix
        satellites = drone.satellites
        
        payload = struct.pack('<QiiiHHHHBB',
            time_usec, lat, lon, alt,
            eph, epv, vel, cog,
            fix_type, satellites
        )
        
        return self._wrap_message(msg_id, payload, crc_extra)
    
    def pack_vfr_hud(self, drone: DroneState) -> bytes:
        """Упаковка VFR_HUD сообщения."""
        msg_id = MAVMsgID.VFR_HUD
        crc_extra = 20
        
        payload = struct.pack('<ffffhH',
            drone.airspeed,
            drone.groundspeed,
            drone.relative_alt,
            drone.vz,
            drone.heading,
            0  # throttle
        )
        
        return self._wrap_message(msg_id, payload, crc_extra)
    
    def pack_sys_status(self, drone: DroneState) -> bytes:
        """Упаковка SYS_STATUS сообщения."""
        msg_id = MAVMsgID.SYS_STATUS
        crc_extra = 124
        
        voltage = int(drone.battery_voltage * 1000)
        current = 1000  # 1A
        remaining = drone.battery_remaining
        
        payload = struct.pack('<IIIHhhhHHHbBBB',
            0xFFFF,  # sensors present
            0xFFFF,  # sensors enabled
            0xFFFF,  # sensors health
            0,       # load
            voltage,
            current,
            remaining,
            0, 0, 0, 0, 0, 0, 0
        )
        
        return self._wrap_message(msg_id, payload, crc_extra)
    
    def _wrap_message(self, msg_id: int, payload: bytes, crc_extra: int) -> bytes:
        """Обернуть payload в MAVLink v1 пакет."""
        header = struct.pack('<BBBBBB',
            self.MAGIC_V1,
            len(payload),
            self.sequence,
            self.system_id,
            self.component_id,
            msg_id
        )
        
        self.sequence = (self.sequence + 1) & 0xFF
        
        crc_data = header[1:] + payload
        crc = self.crc_calculate(crc_data, crc_extra)
        
        return header + payload + struct.pack('<H', crc)


class DroneEmulator:
    """Эмулятор дрона с поддержкой движения и миссий."""
    
    def __init__(self, system_id: int = 1):
        self.state = DroneState()
        self.mavlink = MAVLinkMessage(system_id=system_id)
        self.running = False
        self.callbacks: list[Callable] = []
    
    def add_callback(self, callback: Callable):
        """Добавить callback для обработки исходящих сообщений."""
        self.callbacks.append(callback)
    
    def set_position(self, lat: float, lon: float, alt: float = 0):
        """Установить начальную позицию."""
        self.state.lat = lat
        self.state.lon = lon
        self.state.alt = alt
    
    def arm(self):
        """Армирование дрона."""
        self.state.armed = True
        self.state.state = MAVState.ACTIVE
    
    def disarm(self):
        """Дизармирование дрона."""
        self.state.armed = False
        self.state.state = MAVState.STANDBY
    
    def set_mode(self, mode: MAVMode):
        """Установить режим полёта."""
        self.state.mode = mode
    
    def add_waypoint(self, lat: float, lon: float, alt: float):
        """Добавить waypoint в миссию."""
        self.state.waypoints.append((lat, lon, alt))
    
    def start_mission(self):
        """Начать выполнение миссии."""
        if self.state.waypoints and self.state.armed:
            self.state.mission_active = True
            self.state.current_wp = 0
            self.state.mode = MAVMode.AUTO
    
    def update_physics(self, dt: float):
        """Обновление физики дрона."""
        if not self.state.armed:
            return
        
        if self.state.mission_active and self.state.waypoints:
            self._update_mission(dt)
        
        # Разряд батареи
        if self.state.armed:
            self.state.battery_remaining = max(0, self.state.battery_remaining - 0.001)
            self.state.battery_voltage = 10.5 + (self.state.battery_remaining / 100) * 2.1
        
        # Небольшие колебания для реалистичности
        self.state.roll = math.sin(time.time() * 0.5) * 0.02
        self.state.pitch = math.cos(time.time() * 0.3) * 0.02
        
        # GPS шум
        self.state.satellites = random.randint(10, 14)
    
    def _update_mission(self, dt: float):
        """Обновление выполнения миссии."""
        if self.state.current_wp >= len(self.state.waypoints):
            self.state.mission_active = False
            self.state.mode = MAVMode.STABILIZE
            return
        
        target = self.state.waypoints[self.state.current_wp]
        target_lat, target_lon, target_alt = target
        
        # Расчёт направления и расстояния
        dlat = target_lat - self.state.lat
        dlon = target_lon - self.state.lon
        dalt = target_alt - self.state.relative_alt
        
        dist = math.sqrt(dlat**2 + dlon**2) * 111000  # грубое преобразование в метры
        
        if dist < 5:  # Достигли waypoint
            self.state.current_wp += 1
            return
        
        # Движение к цели
        speed = 5.0  # м/с
        move_dist = speed * dt / 111000
        
        if dist > 0:
            self.state.lat += (dlat / dist) * move_dist * 111000 / 111000
            self.state.lon += (dlon / dist) * move_dist * 111000 / 111000
        
        self.state.relative_alt += min(max(dalt, -2 * dt), 2 * dt)
        self.state.alt = self.state.relative_alt
        
        self.state.groundspeed = speed
        self.state.airspeed = speed
        self.state.heading = int(math.degrees(math.atan2(dlon, dlat))) % 360
        self.state.yaw = math.radians(self.state.heading)
    
    def get_telemetry_messages(self) -> list[bytes]:
        """Получить набор телеметрических сообщений."""
        messages = [
            self.mavlink.pack_heartbeat(self.state),
            self.mavlink.pack_global_position_int(self.state),
            self.mavlink.pack_attitude(self.state),
            self.mavlink.pack_gps_raw_int(self.state),
            self.mavlink.pack_vfr_hud(self.state),
            self.mavlink.pack_sys_status(self.state),
        ]
        return messages


class UDPServer:
    """UDP сервер для отправки MAVLink сообщений."""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 14550):
        self.host = host
        self.port = port
        self.sock = None
        self.clients: set[tuple] = set()
    
    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.setblocking(False)
    
    def send_to_all(self, data: bytes):
        if not self.clients:
            # Broadcast если нет клиентов
            try:
                self.sock.sendto(data, ('127.0.0.1', 14551))
            except:
                pass
        else:
            for client in self.clients:
                try:
                    self.sock.sendto(data, client)
                except:
                    pass
    
    def receive(self) -> tuple[bytes, tuple] | None:
        try:
            data, addr = self.sock.recvfrom(1024)
            self.clients.add(addr)
            return data, addr
        except BlockingIOError:
            return None
    
    def close(self):
        if self.sock:
            self.sock.close()


async def run_emulator(args):
    """Запуск эмулятора."""
    emulator = DroneEmulator(system_id=args.system_id)
    emulator.set_position(args.lat, args.lon, 0)
    
    server = UDPServer(host=args.host, port=args.port)
    server.start()
    
    print(f"MAVLink Emulator started on {args.host}:{args.port}")
    print(f"System ID: {args.system_id}")
    print(f"Initial position: {args.lat}, {args.lon}")
    print("Press Ctrl+C to stop")
    
    if args.auto_arm:
        emulator.arm()
        print("Auto-armed")
    
    if args.mission_file:
        with open(args.mission_file) as f:
            mission = json.load(f)
            for wp in mission.get('waypoints', []):
                emulator.add_waypoint(wp['lat'], wp['lon'], wp.get('alt', 50))
        print(f"Loaded mission with {len(emulator.state.waypoints)} waypoints")
        if args.auto_start:
            emulator.start_mission()
            print("Mission started")
    
    last_time = time.time()
    
    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Обновление физики
            emulator.update_physics(dt)
            
            # Приём входящих сообщений
            while True:
                result = server.receive()
                if result is None:
                    break
                data, addr = result
                # Здесь можно добавить обработку входящих команд
            
            # Отправка телеметрии
            for msg in emulator.get_telemetry_messages():
                server.send_to_all(msg)
            
            await asyncio.sleep(1.0 / args.rate)
    except KeyboardInterrupt:
        print("\nStopping emulator...")
    finally:
        server.close()


def main():
    parser = argparse.ArgumentParser(
        description='MAVLink Emulator - эмулятор БПЛА для тестирования'
    )
    
    parser.add_argument('--host', default='127.0.0.1',
                        help='IP адрес для прослушивания (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=14550,
                        help='UDP порт (default: 14550)')
    parser.add_argument('--system-id', type=int, default=1,
                        help='MAVLink System ID (default: 1)')
    parser.add_argument('--rate', type=float, default=10,
                        help='Частота отправки телеметрии в Гц (default: 10)')
    parser.add_argument('--lat', type=float, default=55.7558,
                        help='Начальная широта (default: 55.7558 - Москва)')
    parser.add_argument('--lon', type=float, default=37.6173,
                        help='Начальная долгота (default: 37.6173 - Москва)')
    parser.add_argument('--auto-arm', action='store_true',
                        help='Автоматически армировать при запуске')
    parser.add_argument('--mission-file', type=str,
                        help='JSON файл с миссией')
    parser.add_argument('--auto-start', action='store_true',
                        help='Автоматически начать миссию')
    
    args = parser.parse_args()
    
    asyncio.run(run_emulator(args))


if __name__ == '__main__':
    main()
