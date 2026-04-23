"""
MAVLink Parser - парсер бинарных MAVLink лог-файлов.

Задание: реализуйте функции для парсинга MAVLink сообщений
и извлечения телеметрических данных.
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
import json
import numpy as np
import math
import struct
from typing import Any


# MAVLink v1 константы
MAVLINK_STX_V1 = 0xFE
MAVLINK_STX_V2 = 0xFD

# Message IDs
MSG_HEARTBEAT = 0
MSG_GPS_RAW_INT = 24
MSG_GLOBAL_POSITION_INT = 33
MSG_VFR_HUD = 74



def parse_mavlink_file(filepath: str) -> list[dict]:
    """
    Парсит бинарный MAVLink файл и возвращает список сообщений.
    
    Каждый MAVLink v1 пакет имеет структуру:
    - STX (1 байт): 0xFE
    - LEN (1 байт): длина payload
    - SEQ (1 байт): sequence number
    - SYS (1 байт): system ID
    - COMP (1 байт): component ID
    - MSG (1 байт): message ID
    - PAYLOAD (LEN байт): данные
    - CRC (2 байта): контрольная сумма
    
    Args:
        filepath: путь к бинарному файлу
        
    Returns:
        Список словарей с полями:
        - msg_id: ID сообщения
        - system_id: ID системы
        - component_id: ID компонента
        - sequence: sequence number
        - payload: байты payload
    """

    messages = []

    # Чтение бинарного файла
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Парсинг файла в список словарей messages
    i = 0
    data_len = len(data)

    while i < data_len:

        # Поиск стартового байта пакета 0xFE
        if data[i] != MAVLINK_STX_V1:
            i += 1
            continue
        
        # Извлекается заголовок header
        # LEN, SEQ, SYS, COMP, MSG, STX не сохраняется
        header = data[i:i+6]
        payload_len = header[1]
        seq = header[2]
        sys_id = header[3]
        comp_id = header[4]
        msg_id = header[5]
        
        # Извлекается полезная нагрузка  payload
        payload_start = i + 6
        payload = data[payload_start:payload_start + payload_len]
        
        # Извлекается контрольная сумма CRC
        crc_start = payload_start + payload_len
        crc = data[crc_start : crc_start + 2][0]
        
        # Добавление в список словарей
        messages.append({
            'payload_len': payload_len,
            'sequence': seq,
            'system_id': sys_id,
            'component_id': comp_id,
            'msg_id': msg_id,
            'payload': payload,
            'crc': crc 
        })

        # Перестановка i на следующий байт после прохода пакета
        header_len = 6
        crc_len = 2
        i = i + header_len + payload_len + crc_len

    return messages


def extract_gps_data(messages: list[dict]) -> list[dict]:
    """
    Извлекает GPS данные из GLOBAL_POSITION_INT сообщений.
    
    Структура GLOBAL_POSITION_INT payload (28 байт):
    - time_boot_ms (uint32): время в мс
    - lat (int32): широта * 1e7
    - lon (int32): долгота * 1e7
    - alt (int32): абсолютная высота в мм
    - relative_alt (int32): относительная высота в мм
    - vx (int16): скорость X в см/с
    - vy (int16): скорость Y в см/с
    - vz (int16): скорость Z в см/с
    - hdg (uint16): курс в сотых долях градуса
    
    Args:
        messages: список сообщений от parse_mavlink_file()
        
    Returns:
        Список словарей с полями:
        - timestamp: время в секундах
        - lat: широта в градусах
        - lon: долгота в градусах
        - alt: высота в метрах
        - relative_alt: относительная высота в метрах
    """
    
    gps_data = []
    
    # Распаковка сообщений только с индентификатором равным MSG_GLOBAL_POSITION_INT
    for msg in messages:
        if msg['msg_id'] != MSG_GLOBAL_POSITION_INT:  
            continue

        payload = msg['payload']

        # Распаковка с little-endian
        (time_boot_ms, lat, lon, alt, relative_alt, vx, vy, vz, hdg) = struct.unpack('<IiiiihhhH', payload)

        # Преобразование в физические величины и добавление в список словаря
        gps_entry = {
            'timestamp': time_boot_ms / 1000.0,        
            'lat': lat / 1e7,                           
            'lon': lon / 1e7,                           
            'alt': alt / 1000.0,                         
            'relative_alt': relative_alt / 1000.0        
        }
        gps_data.append(gps_entry)
    
    return gps_data


def extract_speed_data(messages: list[dict]) -> list[dict]:
    """
    Извлекает данные о скорости из VFR_HUD сообщений.
    
    Структура VFR_HUD payload (20 байт):
    - airspeed (float): воздушная скорость м/с
    - groundspeed (float): наземная скорость м/с
    - alt (float): высота м
    - climb (float): вертикальная скорость м/с
    - heading (int16): курс в градусах
    - throttle (uint16): газ в %
    
    Args:
        messages: список сообщений от parse_mavlink_file()
        
    Returns:
        Список словарей с полями:
        - airspeed: воздушная скорость м/с
        - groundspeed: наземная скорость м/с
        - climb: вертикальная скорость м/с
        - heading: курс в градусах
    """

    speed_data = []
    
    # Распаковка сообщений только с индентификатором равным MSG_VFR_HUD
    for msg in messages:
        if(msg['msg_id'] != MSG_VFR_HUD):
            continue
    
        payload = msg['payload']

        # Распаковка с little-endian
        (airspeed, groundspeed, alt, climb, heading, throttle) = struct.unpack('<ffffhH', payload)

        # Преобразование в словарь и добавление словаря в список
        stat = {
            'airspeed' : airspeed,
            'groundspeed' : groundspeed,
            'alt' : alt,
            'climb' : climb,
            'heading' : heading,
            'throttle' : throttle,
        }
        
        speed_data.append(stat)
    
    return speed_data


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Вычисляет расстояние между двумя GPS точками по формуле Хаверсина.
    
    Args:
        lat1, lon1: координаты первой точки в градусах
        lat2, lon2: координаты второй точки в градусах
        
    Returns:
        Расстояние в метрах
    """
    R = 6371000  # Радиус Земли в метрах
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def calculate_flight_stats(gps_data: list[dict], speed_data: list[dict]) -> dict:
    """
    Вычисляет статистику полёта.
    
    Args:
        gps_data: данные GPS от extract_gps_data()
        speed_data: данные скорости от extract_speed_data()
        
    Returns:
        Словарь с полями:
        - max_altitude: максимальная относительная высота (м)
        - min_altitude: минимальная относительная высота (м)
        - avg_speed: средняя скорость (м/с)
        - max_speed: максимальная скорость (м/с)
        - distance: общее пройденное расстояние (м)
        - duration: длительность полёта (с)
    """
    
    stats = {
        'max_altitude': 0.0,
        'min_altitude': 0.0,
        'avg_speed': 0.0,
        'max_speed': 0.0,
        'distance': 0.0,
        'duration': 0.0,
    }

    # Нахождение наибольшей высоты
    max_altitude = 0.0
    for gps in gps_data:
        if max_altitude < gps['relative_alt']:
            max_altitude = gps['relative_alt']
    stats['max_altitude'] = max_altitude
    
    # Наименьшая высота
    min_altitude = max_altitude
    for gps in gps_data:
        if min_altitude < gps['relative_alt']:
            min_altitude = gps['relative_alt']
    stats['min_altitude'] = min_altitude

    # Средняя скорость
    speed_sum = 0
    if len(speed_data) != 0:
        for speed in speed_data:
            speed_sum += speed['groundspeed']
        avg_speed = speed_sum / len(speed_data)
        stats['avg_speed'] = avg_speed

    # Наибольшая скорость
    max_speed = 0.0
    for speed in speed_data:
        if max_speed < speed['groundspeed']:
            max_speed = speed['groundspeed']
    stats['max_speed'] = max_speed

    # Общее пройденное расстояние
    size_gps = len(gps_data)
    distance = 0.0
    for i in range (1, size_gps):
        gps_start = gps_data[i - 1]
        gps_end = gps_data[i]
        distance = distance + haversine_distance(gps_start['lat'], gps_start['lon'], gps_end['lat'], gps_end['lon'])
    stats['distance'] = distance

    # Общее время полета
    if len(gps_data) > 1:
        timestamp = gps_data[len(gps_data) - 1]['timestamp'] - gps_data[0]['timestamp']

    return stats

def visualize_flight_3d(gps_data):
    """ Построение графика
    
    Args:
        gps_data: данные GPS от extract_gps_data()
        
    Returns:
        None
    """
    
    # Создание списков
    # Извлечение долготы ширины высоты
    lons = [data['lon'] for data in gps_data]
    lats = [data['lat'] for data in gps_data]
    alts = [data['relative_alt'] for data in gps_data]
    
    # Создание графика
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Долгота, ширина, высота, жирность линии, цвет
    ax.plot(lons, lats, alts, linewidth=2, color='blue')
    
    # Подписи осей
    ax.set_xlabel('Долгота')
    ax.set_ylabel('Широта')
    ax.set_zlabel('Высота (м)')
    ax.set_title('Траектория полёта')
    
    plt.show()

def export_to_geojson_simple(gps_data, output_file):
    """Создание GeoJson
    
    Args:
        gps_data: данные GPS от extract_gps_data()
        output_file: строка, название файла

    Returns:
        None
    """

    # Список из долготы, ширины, высоты
    coordinates = [[data['lon'], data['lat'], data['relative_alt']] for data in gps_data]
    

    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates
        },
        "properties": {
            "name": "Траектория полёта"
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"Сохранено в {output_file}")

def main():
    """Пример использования парсера."""
    import os
    
    # Путь к тестовому файлу
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    log_file = os.path.join(data_dir, 'mavlink_log.bin')
    
    if not os.path.exists(log_file):
        print(f"Файл {log_file} не найден")
        print("Скопируйте mavlink_log.bin из common/test-data/")
        return
    
    # Парсинг файла
    messages = parse_mavlink_file(log_file)
    print(f"Прочитано сообщений: {len(messages)}")
    
    # Извлечение данных
    gps_data = extract_gps_data(messages)
    speed_data = extract_speed_data(messages)
    print(f"GPS точек: {len(gps_data)}")
    print(f"Данных скорости: {len(speed_data)}")
    
    # Статистика
    stats = calculate_flight_stats(gps_data, speed_data)
    print("\nСтатистика полёта:")
    print(f"  Макс. высота: {stats['max_altitude']:.1f} м")
    print(f"  Средняя скорость: {stats['avg_speed']:.1f} м/с")
    print(f"  Макс. скорость: {stats['max_speed']:.1f} м/с")
    print(f"  Пройдено: {stats['distance']:.1f} м")

    #ДОПОЛНИТЕЛЬНЫЙ БЛОК

    # Экспорт в GeoJSON траектории дрона
    export_to_geojson_simple(gps_data, 'DroneMap.geojson')

    # Визуализация
    visualize_flight_3d(gps_data)

if __name__ == '__main__':
    main()
