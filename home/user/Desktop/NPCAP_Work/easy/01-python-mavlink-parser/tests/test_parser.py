"""Тесты для MAVLink парсера."""

import os
import sys
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser import (
    parse_mavlink_file,
    extract_gps_data,
    extract_speed_data,
    calculate_flight_stats,
    haversine_distance,
    MSG_GLOBAL_POSITION_INT,
    MSG_VFR_HUD,
    MSG_HEARTBEAT,
)


def get_test_data_path():
    """Получить путь к тестовым данным."""
    return os.path.join(os.path.dirname(__file__), '..', 'data', 'mavlink_log.bin')


class TestParseMAVLinkFile:
    """Тесты для parse_mavlink_file."""
    
    def test_parse_returns_list(self):
        """Функция должна возвращать список."""
        filepath = get_test_data_path()
        if not os.path.exists(filepath):
            import pytest
            pytest.skip("Test data not found")
        
        result = parse_mavlink_file(filepath)
        assert isinstance(result, list)
    
    def test_parse_returns_nonempty(self):
        """Функция должна возвращать непустой список."""
        filepath = get_test_data_path()
        if not os.path.exists(filepath):
            import pytest
            pytest.skip("Test data not found")
        
        result = parse_mavlink_file(filepath)
        assert len(result) > 0
    
    def test_message_structure(self):
        """Каждое сообщение должно иметь нужные поля."""
        filepath = get_test_data_path()
        if not os.path.exists(filepath):
            import pytest
            pytest.skip("Test data not found")
        
        result = parse_mavlink_file(filepath)
        if len(result) > 0:
            msg = result[0]
            assert 'msg_id' in msg
            assert 'system_id' in msg
            assert 'component_id' in msg
            assert 'payload' in msg
    
    def test_contains_expected_message_types(self):
        """Файл должен содержать ожидаемые типы сообщений."""
        filepath = get_test_data_path()
        if not os.path.exists(filepath):
            import pytest
            pytest.skip("Test data not found")
        
        result = parse_mavlink_file(filepath)
        msg_ids = {msg['msg_id'] for msg in result}
        
        assert MSG_GLOBAL_POSITION_INT in msg_ids, "Should contain GLOBAL_POSITION_INT"
        assert MSG_VFR_HUD in msg_ids, "Should contain VFR_HUD"


class TestExtractGPSData:
    """Тесты для extract_gps_data."""
    
    def test_returns_list(self):
        """Функция должна возвращать список."""
        result = extract_gps_data([])
        assert isinstance(result, list)
    
    def test_extracts_coordinates(self):
        """Должна извлекать координаты из GLOBAL_POSITION_INT."""
        # Создаём тестовое сообщение
        lat = int(55.7558 * 1e7)
        lon = int(37.6173 * 1e7)
        alt = 150000  # 150m в мм
        rel_alt = 50000  # 50m в мм
        
        payload = struct.pack('<IiiiihhhH',
            1000,  # time_boot_ms
            lat, lon, alt, rel_alt,
            100, 100, 0,  # vx, vy, vz
            9000  # hdg
        )
        
        messages = [{
            'msg_id': MSG_GLOBAL_POSITION_INT,
            'system_id': 1,
            'component_id': 1,
            'payload': payload
        }]
        
        result = extract_gps_data(messages)
        
        assert len(result) == 1
        assert abs(result[0]['lat'] - 55.7558) < 0.0001
        assert abs(result[0]['lon'] - 37.6173) < 0.0001
        assert abs(result[0]['alt'] - 150.0) < 0.1
        assert abs(result[0]['relative_alt'] - 50.0) < 0.1


class TestExtractSpeedData:
    """Тесты для extract_speed_data."""
    
    def test_returns_list(self):
        """Функция должна возвращать список."""
        result = extract_speed_data([])
        assert isinstance(result, list)
    
    def test_extracts_speed(self):
        """Должна извлекать скорость из VFR_HUD."""
        payload = struct.pack('<ffffhH',
            10.5,  # airspeed
            9.8,   # groundspeed
            50.0,  # alt
            2.5,   # climb
            90,    # heading
            50     # throttle
        )
        
        messages = [{
            'msg_id': MSG_VFR_HUD,
            'system_id': 1,
            'component_id': 1,
            'payload': payload
        }]
        
        result = extract_speed_data(messages)
        
        assert len(result) == 1
        assert abs(result[0]['airspeed'] - 10.5) < 0.01
        assert abs(result[0]['groundspeed'] - 9.8) < 0.01
        assert abs(result[0]['climb'] - 2.5) < 0.01
        assert result[0]['heading'] == 90


class TestHaversineDistance:
    """Тесты для haversine_distance."""
    
    def test_same_point_zero_distance(self):
        """Расстояние между одинаковыми точками = 0."""
        dist = haversine_distance(55.7558, 37.6173, 55.7558, 37.6173)
        assert abs(dist) < 0.01
    
    def test_known_distance(self):
        """Проверка на известном расстоянии (Москва - Санкт-Петербург ~635 км)."""
        moscow_lat, moscow_lon = 55.7558, 37.6173
        spb_lat, spb_lon = 59.9343, 30.3351
        
        dist = haversine_distance(moscow_lat, moscow_lon, spb_lat, spb_lon)
        
        # Расстояние должно быть около 635 км (допуск 10 км)
        assert 625000 < dist < 645000


class TestCalculateFlightStats:
    """Тесты для calculate_flight_stats."""
    
    def test_returns_dict(self):
        """Функция должна возвращать словарь."""
        result = calculate_flight_stats([], [])
        assert isinstance(result, dict)
    
    def test_contains_required_fields(self):
        """Словарь должен содержать все необходимые поля."""
        result = calculate_flight_stats([], [])
        
        assert 'max_altitude' in result
        assert 'min_altitude' in result
        assert 'avg_speed' in result
        assert 'max_speed' in result
        assert 'distance' in result
        assert 'duration' in result
    
    def test_calculates_max_altitude(self):
        """Должна правильно вычислять максимальную высоту."""
        gps_data = [
            {'relative_alt': 10.0, 'lat': 55.755, 'lon': 37.617, 'timestamp': 0},
            {'relative_alt': 50.0, 'lat': 55.756, 'lon': 37.618, 'timestamp': 1},
            {'relative_alt': 30.0, 'lat': 55.757, 'lon': 37.619, 'timestamp': 2},
        ]
        speed_data = [
            {'groundspeed': 5.0},
            {'groundspeed': 10.0},
            {'groundspeed': 7.0},
        ]
        
        result = calculate_flight_stats(gps_data, speed_data)
        
        assert result['max_altitude'] == 50.0
    
    def test_calculates_avg_speed(self):
        """Должна правильно вычислять среднюю скорость."""
        gps_data = []
        speed_data = [
            {'groundspeed': 5.0},
            {'groundspeed': 10.0},
            {'groundspeed': 15.0},
        ]
        
        result = calculate_flight_stats(gps_data, speed_data)
        
        assert abs(result['avg_speed'] - 10.0) < 0.01
