#!/usr/bin/env python3
"""Генератор тестового MAVLink лог-файла."""

import struct
import time


def crc_accumulate(byte: int, crc: int) -> int:
    tmp = byte ^ (crc & 0xFF)
    tmp ^= (tmp << 4) & 0xFF
    return ((crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)) & 0xFFFF


def crc_calculate(data: bytes, crc_extra: int) -> int:
    crc = 0xFFFF
    for b in data:
        crc = crc_accumulate(b, crc)
    crc = crc_accumulate(crc_extra, crc)
    return crc


def pack_message(seq: int, sys_id: int, comp_id: int, msg_id: int, 
                 payload: bytes, crc_extra: int) -> bytes:
    """Упаковать MAVLink v1 сообщение."""
    header = struct.pack('<BBBBBB',
        0xFE,  # magic
        len(payload),
        seq & 0xFF,
        sys_id,
        comp_id,
        msg_id
    )
    
    crc_data = header[1:] + payload
    crc = crc_calculate(crc_data, crc_extra)
    
    return header + payload + struct.pack('<H', crc)


def generate_heartbeat(seq: int) -> bytes:
    """HEARTBEAT сообщение."""
    payload = struct.pack('<IBBBBB',
        88,   # custom_mode (GUIDED)
        2,    # type (quadrotor)
        3,    # autopilot (ardupilot)
        0x90, # base_mode (armed + guided)
        4,    # system_status (active)
        3     # mavlink_version
    )
    return pack_message(seq, 1, 1, 0, payload, 50)


def generate_global_position(seq: int, lat: float, lon: float, 
                             alt: float, rel_alt: float, 
                             vx: float, vy: float, vz: float, hdg: int) -> bytes:
    """GLOBAL_POSITION_INT сообщение."""
    time_boot_ms = int(time.time() * 1000) & 0xFFFFFFFF
    
    payload = struct.pack('<IiiiihhhH',
        time_boot_ms,
        int(lat * 1e7),
        int(lon * 1e7),
        int(alt * 1000),
        int(rel_alt * 1000),
        int(vx * 100),
        int(vy * 100),
        int(vz * 100),
        int(hdg * 100)
    )
    return pack_message(seq, 1, 1, 33, payload, 104)


def generate_gps_raw(seq: int, lat: float, lon: float, alt: float,
                     speed: float, hdg: int, sats: int) -> bytes:
    """GPS_RAW_INT сообщение."""
    time_usec = int(time.time() * 1e6)
    
    payload = struct.pack('<QiiiHHHHBB',
        time_usec,
        int(lat * 1e7),
        int(lon * 1e7),
        int(alt * 1000),
        100,  # eph
        100,  # epv
        int(speed * 100),
        int(hdg * 100),
        3,    # fix_type
        sats
    )
    return pack_message(seq, 1, 1, 24, payload, 24)


def generate_vfr_hud(seq: int, airspeed: float, groundspeed: float,
                     alt: float, climb: float, heading: int) -> bytes:
    """VFR_HUD сообщение."""
    payload = struct.pack('<ffffhH',
        airspeed,
        groundspeed,
        alt,
        climb,
        heading,
        50  # throttle
    )
    return pack_message(seq, 1, 1, 74, payload, 20)


def main():
    """Генерация тестового лог-файла."""
    messages = []
    seq = 0
    
    # Начальные координаты (Москва)
    lat = 55.7558
    lon = 37.6173
    alt = 150.0
    rel_alt = 0.0
    
    # Генерация 100 сообщений с имитацией полёта
    for i in range(100):
        # Heartbeat каждые 10 итераций
        if i % 10 == 0:
            messages.append(generate_heartbeat(seq))
            seq += 1
        
        # Набор высоты первые 20 итераций
        if i < 20:
            rel_alt = min(50.0, rel_alt + 2.5)
            speed = 3.0 + i * 0.2
        else:
            # Горизонтальный полёт
            lat += 0.00005
            lon += 0.00008
            speed = 10.0
        
        hdg = 45 + i % 90
        sats = 10 + (i % 5)
        
        messages.append(generate_global_position(
            seq, lat, lon, alt + rel_alt, rel_alt,
            speed * 0.7, speed * 0.7, 0.0 if i >= 20 else 2.0, hdg
        ))
        seq += 1
        
        messages.append(generate_gps_raw(seq, lat, lon, alt + rel_alt, speed, hdg, sats))
        seq += 1
        
        messages.append(generate_vfr_hud(seq, speed, speed * 0.95, rel_alt, 
                                         0.0 if i >= 20 else 2.5, hdg))
        seq += 1
    
    # Запись в файл
    with open('mavlink_log.bin', 'wb') as f:
        for msg in messages:
            f.write(msg)
    
    print(f"Generated mavlink_log.bin with {len(messages)} messages")
    print(f"Total size: {sum(len(m) for m in messages)} bytes")


if __name__ == '__main__':
    main()
