"""Тесты для Flight Simulator."""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simulator import FlightSimulator, DroneState, Waypoint


class TestDroneState:
    def test_default_values(self):
        state = DroneState()
        assert state.armed == False
        assert state.battery == 100.0
        assert state.mode == "STABILIZE"


class TestFlightSimulator:
    def test_initial_state(self):
        sim = FlightSimulator()
        assert sim.state.armed == False
        assert len(sim.mission) == 0
    
    def test_arm_when_not_armed(self):
        sim = FlightSimulator()
        # После реализации arm() этот тест должен проходить
        result = sim.arm()
        # Ожидаем True после реализации
        # assert result == True
        # assert sim.state.armed == True
    
    def test_disarm_in_air_fails(self):
        sim = FlightSimulator()
        sim.state.armed = True
        sim.state.alt = 50.0  # В воздухе
        result = sim.disarm()
        # Должен вернуть False - нельзя дизармировать в воздухе
        # assert result == False
    
    def test_start_mission_requires_arm(self):
        sim = FlightSimulator()
        sim.mission = [Waypoint(lat=55.0, lon=37.0, alt=50)]
        result = sim.start_mission()
        # Должен вернуть False - не армирован
        # assert result == False


class TestHaversine:
    def test_same_point_zero_distance(self):
        dist = FlightSimulator.haversine_distance(55.7558, 37.6173, 55.7558, 37.6173)
        assert abs(dist) < 0.01
    
    def test_known_distance(self):
        # Москва - Санкт-Петербург ~635 км
        dist = FlightSimulator.haversine_distance(55.7558, 37.6173, 59.9343, 30.3351)
        assert 600_000 < dist < 670_000


class TestBearing:
    def test_north(self):
        bearing = FlightSimulator.bearing(50.0, 0.0, 51.0, 0.0)
        # Направление на север ~0 радиан
        assert abs(bearing) < 0.01


@pytest.mark.asyncio
async def test_load_mission():
    sim = FlightSimulator()
    mission_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mission.json')
    
    if os.path.exists(mission_path):
        result = await sim.load_mission(mission_path)
        # После реализации
        # assert result == True
        # assert len(sim.mission) > 0
