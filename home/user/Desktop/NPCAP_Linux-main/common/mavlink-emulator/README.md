# MAVLink Emulator

Эмулятор БПЛА для тестирования заданий без реального оборудования.

## Установка

```bash
pip install -r requirements.txt
```

## Использование

### Базовый запуск

```bash
python emulator.py
```

Эмулятор запустится на `127.0.0.1:14550` и начнёт отправлять телеметрию.

### Параметры запуска

```bash
python emulator.py --help

Options:
  --host HOST          IP адрес (default: 127.0.0.1)
  --port PORT          UDP порт (default: 14550)
  --system-id ID       MAVLink System ID (default: 1)
  --rate HZ            Частота телеметрии (default: 10)
  --lat LAT            Начальная широта (default: 55.7558)
  --lon LON            Начальная долгота (default: 37.6173)
  --auto-arm           Автоматически армировать
  --mission-file FILE  JSON файл с миссией
  --auto-start         Автоматически начать миссию
```

### Примеры

Запуск с автоматическим армированием:
```bash
python emulator.py --auto-arm
```

Запуск с миссией:
```bash
python emulator.py --auto-arm --mission-file mission.json --auto-start
```

## Формат файла миссии

```json
{
  "waypoints": [
    {"lat": 55.7560, "lon": 37.6180, "alt": 50},
    {"lat": 55.7570, "lon": 37.6190, "alt": 100},
    {"lat": 55.7565, "lon": 37.6175, "alt": 50}
  ]
}
```

## Поддерживаемые MAVLink сообщения

### Исходящие (телеметрия)
- `HEARTBEAT` (ID: 0) - статус системы
- `SYS_STATUS` (ID: 1) - состояние батареи и датчиков
- `GPS_RAW_INT` (ID: 24) - сырые GPS данные
- `ATTITUDE` (ID: 30) - крен, тангаж, рысканье
- `GLOBAL_POSITION_INT` (ID: 33) - глобальная позиция
- `VFR_HUD` (ID: 74) - данные для HUD

### Входящие (команды)
- В текущей версии команды логируются, но не обрабатываются

## Подключение клиента

### Python (pymavlink)

```python
from pymavlink import mavutil

conn = mavutil.mavlink_connection('udpin:127.0.0.1:14551')
while True:
    msg = conn.recv_match(blocking=True)
    print(msg)
```

### Прослушивание телеметрии

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 14551))

# Отправить что-то эмулятору чтобы зарегистрироваться
sock.sendto(b'', ('127.0.0.1', 14550))

while True:
    data, addr = sock.recvfrom(1024)
    print(f"Received {len(data)} bytes")
```

## Архитектура

```
┌─────────────────┐
│  DroneEmulator  │
│  ┌───────────┐  │
│  │DroneState │  │  состояние дрона
│  └───────────┘  │
│  ┌───────────┐  │
│  │MAVLinkMsg │  │  формирование пакетов
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   UDPServer     │  отправка по UDP
└────────┬────────┘
         │
         ▼
    Клиенты (GCS)
```
