#!/usr/bin/env python3
"""Утилита для отправки команд симулятору."""

import argparse
import json
import socket


def send_command(host: str, port: int, command: dict):
    """Отправить команду симулятору."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        data = json.dumps(command).encode()
        sock.sendto(data, (host, port))
        print(f"Sent: {command}")
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description='Flight Simulator Commander')
    parser.add_argument('command', choices=['arm', 'disarm', 'start', 'pause', 'resume', 'goto', 'rtl', 'land'])
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=14551)
    parser.add_argument('--lat', type=float, help='Latitude for goto command')
    parser.add_argument('--lon', type=float, help='Longitude for goto command')
    parser.add_argument('--alt', type=float, help='Altitude for goto command')
    
    args = parser.parse_args()
    
    if args.command == 'goto':
        if not all([args.lat, args.lon, args.alt]):
            print("Error: goto requires --lat, --lon, --alt")
            return
        cmd = {'command': 'goto', 'lat': args.lat, 'lon': args.lon, 'alt': args.alt}
    else:
        cmd = {'command': args.command}
    
    send_command(args.host, args.port, cmd)


if __name__ == '__main__':
    main()
