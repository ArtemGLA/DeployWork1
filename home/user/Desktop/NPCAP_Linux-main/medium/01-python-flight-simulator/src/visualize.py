#!/usr/bin/env python3
"""Простой слушатель телеметрии."""

import socket
import struct

def decode_mavlink(data):
    """Декодировать основные поля MAVLink."""
    if len(data) < 8:
        return None
    
    magic = data[0]
    if magic != 0xFE:
        return None
    
    msg_len = data[1]
    msg_id = data[5]
    
    if msg_id == 33 and len(data) >= 6 + msg_len:  # GLOBAL_POSITION_INT
        # Пропускаем заголовок (6 байт) и берём payload
        payload = data[6:6+msg_len]
        if len(payload) >= 28:
            # Распаковываем координаты
            lat, lon, alt_abs, alt_rel = struct.unpack('<iiii', payload[4:20])
            return {
                'type': 'GLOBAL_POSITION_INT',
                'lat': lat / 1e7,
                'lon': lon / 1e7,
                'alt': alt_abs / 1000
            }
    elif msg_id == 74 and len(data) >= 6 + msg_len:  # VFR_HUD
        payload = data[6:6+msg_len]
        if len(payload) >= 20:
            airspeed, groundspeed, alt, climb = struct.unpack('<ffff', payload[:16])
            heading = struct.unpack('<h', payload[16:18])[0]
            return {
                'type': 'VFR_HUD',
                'airspeed': airspeed,
                'groundspeed': groundspeed,
                'alt': alt,
                'climb': climb,
                'heading': heading
            }
    elif msg_id == 0:  # HEARTBEAT
        return {'type': 'HEARTBEAT'}
    
    return None

def main():
    # Создаём UDP сокет
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 14550))  # Слушаем порт 14550
    
    print("📡 Listening for telemetry on port 14550...")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            decoded = decode_mavlink(data)
            
            if decoded:
                if decoded['type'] == 'GLOBAL_POSITION_INT':
                    print(f"📍 Position: lat={decoded['lat']:.4f}, "
                          f"lon={decoded['lon']:.4f}, "
                          f"alt={decoded['alt']:.1f}m")
                elif decoded['type'] == 'VFR_HUD':
                    print(f"✈️  Flight: speed={decoded['groundspeed']:.1f}m/s, "
                          f"heading={decoded['heading']}°, "
                          f"climb={decoded['climb']:.1f}m/s")
            else:
                print(f"📦 Raw MAVLink packet: {len(data)} bytes from {addr}")
                
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()