"""Тесты для анализатора полётных логов."""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analyzer import (
    load_flight_log,
    detect_altitude_anomalies,
    detect_gps_anomalies,
    detect_battery_anomalies,
    detect_speed_anomalies,
    detect_attitude_anomalies,
    generate_report,
)


def get_test_data_path():
    return os.path.join(os.path.dirname(__file__), '..', 'data', 'flight_log.csv')


class TestLoadFlightLog:
    def test_returns_dataframe(self):
        filepath = get_test_data_path()
        if not os.path.exists(filepath):
            import pytest
            pytest.skip("Test data not found")
        
        result = load_flight_log(filepath)
        assert isinstance(result, pd.DataFrame)
    
    def test_has_required_columns(self):
        filepath = get_test_data_path()
        if not os.path.exists(filepath):
            import pytest
            pytest.skip("Test data not found")
        
        df = load_flight_log(filepath)
        required = ['timestamp', 'lat', 'lon', 'alt', 'relative_alt',
                    'groundspeed', 'battery_voltage', 'satellites']
        for col in required:
            assert col in df.columns, f"Missing column: {col}"


class TestDetectAltitudeAnomalies:
    def test_returns_list(self):
        df = pd.DataFrame({
            'timestamp': [1, 2, 3],
            'relative_alt': [10, 20, 30]
        })
        result = detect_altitude_anomalies(df)
        assert isinstance(result, list)
    
    def test_detects_rapid_change(self):
        df = pd.DataFrame({
            'timestamp': [1, 2, 3],
            'relative_alt': [10.0, 25.0, 30.0]  # +15m at t=2
        })
        result = detect_altitude_anomalies(df, threshold=10.0)
        assert len(result) >= 1
        
        anomaly = result[0]
        assert 'timestamp' in anomaly
        assert 'old_value' in anomaly
        assert 'new_value' in anomaly
    
    def test_no_false_positives(self):
        df = pd.DataFrame({
            'timestamp': [1, 2, 3, 4],
            'relative_alt': [10.0, 12.0, 14.0, 16.0]  # gradual change
        })
        result = detect_altitude_anomalies(df, threshold=10.0)
        assert len(result) == 0


class TestDetectGpsAnomalies:
    def test_returns_list(self):
        df = pd.DataFrame({
            'timestamp': [1, 2],
            'satellites': [12, 12],
            'gps_fix': [3, 3]
        })
        result = detect_gps_anomalies(df)
        assert isinstance(result, list)
    
    def test_detects_low_satellites(self):
        df = pd.DataFrame({
            'timestamp': [1, 2, 3],
            'satellites': [12, 4, 12],  # low at t=2
            'gps_fix': [3, 3, 3]
        })
        result = detect_gps_anomalies(df, min_satellites=6)
        assert len(result) >= 1
    
    def test_detects_fix_loss(self):
        df = pd.DataFrame({
            'timestamp': [1, 2, 3],
            'satellites': [12, 12, 12],
            'gps_fix': [3, 2, 3]  # fix degraded at t=2
        })
        result = detect_gps_anomalies(df)
        assert len(result) >= 1


class TestDetectBatteryAnomalies:
    def test_returns_list(self):
        df = pd.DataFrame({
            'timestamp': [1],
            'battery_voltage': [12.0],
            'battery_remaining': [80]
        })
        result = detect_battery_anomalies(df)
        assert isinstance(result, list)
    
    def test_detects_low_voltage(self):
        df = pd.DataFrame({
            'timestamp': [1, 2, 3],
            'battery_voltage': [12.0, 10.0, 12.0],  # low at t=2
            'battery_remaining': [80, 80, 80]
        })
        result = detect_battery_anomalies(df, min_voltage=10.5)
        assert len(result) >= 1


class TestDetectSpeedAnomalies:
    def test_returns_list(self):
        df = pd.DataFrame({
            'timestamp': [1],
            'groundspeed': [10.0]
        })
        result = detect_speed_anomalies(df)
        assert isinstance(result, list)
    
    def test_detects_overspeed(self):
        df = pd.DataFrame({
            'timestamp': [1, 2, 3],
            'groundspeed': [15.0, 25.0, 15.0]  # overspeed at t=2
        })
        result = detect_speed_anomalies(df, max_speed=20.0)
        assert len(result) >= 1


class TestGenerateReport:
    def test_returns_string(self):
        anomalies = {
            'altitude': [],
            'gps': [],
            'battery': [],
            'speed': [],
            'attitude': []
        }
        result = generate_report(anomalies)
        assert isinstance(result, str)
    
    def test_contains_header(self):
        anomalies = {'altitude': []}
        result = generate_report(anomalies)
        assert 'REPORT' in result
    
    def test_lists_anomalies(self):
        anomalies = {
            'altitude': [{'timestamp': 123, 'old_value': 10, 'new_value': 25, 'change': 15}]
        }
        result = generate_report(anomalies)
        assert '123' in result or 'ALTITUDE' in result
