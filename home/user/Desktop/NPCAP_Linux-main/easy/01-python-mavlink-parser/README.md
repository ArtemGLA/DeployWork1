# Задание 1: MAVLink Parser

**Уровень:** Лёгкий  
**Технологии:** Python, pymavlink  
**Время выполнения:** 2-3 часа

## Описание

MAVLink — это легковесный протокол связи для беспилотных систем. Он используется для обмена данными между дроном и наземной станцией управления.

В этом задании вам нужно написать парсер, который читает бинарный MAVLink лог-файл и извлекает из него телеметрические данные.

## Цель

Реализовать функции в файле `src/parser.py`, которые:

1. Читают бинарный MAVLink файл
2. Извлекают GPS координаты (широта, долгота, высота)
3. Извлекают скорость (groundspeed, airspeed)
4. Вычисляют статистику полёта (макс. высота, средняя скорость, длительность)

## Входные данные

Бинарный файл `data/mavlink_log.bin` содержит записанные MAVLink сообщения. Основные типы сообщений:

- `GLOBAL_POSITION_INT` (ID: 33) — GPS координаты
- `GPS_RAW_INT` (ID: 24) — сырые GPS данные
- `VFR_HUD` (ID: 74) — данные для HUD (скорость, высота)
- `HEARTBEAT` (ID: 0) — статус системы

## Структура MAVLink v1 пакета

```
| STX | LEN | SEQ | SYS | COMP | MSG | PAYLOAD... | CRC_L | CRC_H |
|  1  |  1  |  1  |  1  |   1  |  1  |   0-255   |   1   |   1   |
```

- **STX**: стартовый байт (0xFE для MAVLink v1)
- **LEN**: длина payload
- **SEQ**: sequence number
- **SYS**: system ID
- **COMP**: component ID
- **MSG**: message ID
- **PAYLOAD**: данные сообщения
- **CRC**: контрольная сумма

## Что нужно реализовать

Откройте `src/parser.py` и реализуйте следующие функции:

```python
def parse_mavlink_file(filepath: str) -> list[dict]:
    """
    Парсит бинарный MAVLink файл.
    
    Returns:
        Список словарей с данными сообщений
    """
    pass

def extract_gps_data(messages: list[dict]) -> list[dict]:
    """
    Извлекает GPS данные из сообщений.
    
    Returns:
        Список словарей с lat, lon, alt, timestamp
    """
    pass

def extract_speed_data(messages: list[dict]) -> list[dict]:
    """
    Извлекает данные о скорости.
    
    Returns:
        Список словарей с groundspeed, airspeed, timestamp
    """
    pass

def calculate_flight_stats(gps_data: list, speed_data: list) -> dict:
    """
    Вычисляет статистику полёта.
    
    Returns:
        Словарь с max_altitude, avg_speed, duration, distance
    """
    pass
```

## Пример использования

```python
from parser import parse_mavlink_file, extract_gps_data, calculate_flight_stats

messages = parse_mavlink_file('data/mavlink_log.bin')
gps_data = extract_gps_data(messages)
speed_data = extract_speed_data(messages)
stats = calculate_flight_stats(gps_data, speed_data)

print(f"Максимальная высота: {stats['max_altitude']:.1f} м")
print(f"Средняя скорость: {stats['avg_speed']:.1f} м/с")
print(f"Пройденное расстояние: {stats['distance']:.1f} м")
```

## Подсказки

1. Используйте `struct.unpack()` для распаковки бинарных данных
2. Координаты в MAVLink хранятся как int32 * 1e7 (для lat/lon) и mm (для alt)
3. Скорость хранится в см/с
4. Для расчёта расстояния между GPS точками используйте формулу Хаверсина

## Запуск тестов

```bash
cd easy/01-python-mavlink-parser
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Критерии оценки

- [ ] Корректный парсинг MAVLink пакетов
- [ ] Правильное извлечение GPS данных
- [ ] Правильное извлечение данных о скорости
- [ ] Корректный расчёт статистики
- [ ] Код проходит все тесты
- [ ] Читаемый и документированный код

## Дополнительно (необязательно)

- Добавить поддержку MAVLink v2
- Визуализация траектории полёта (matplotlib)
- Экспорт данных в GeoJSON
