"""Тесты для Waypoint Optimizer."""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from optimizer import (
    haversine_distance,
    calculate_distance_matrix,
    route_distance,
    nearest_neighbor,
    two_opt,
    optimize_route,
)


class TestHaversine:
    def test_same_point(self):
        dist = haversine_distance(55.7558, 37.6173, 55.7558, 37.6173)
        assert dist < 0.01
    
    def test_known_distance(self):
        # Москва - СПб ~635 км
        dist = haversine_distance(55.7558, 37.6173, 59.9343, 30.3351)
        assert 600_000 < dist < 670_000
    
    def test_small_distance(self):
        # ~100м
        dist = haversine_distance(55.7558, 37.6173, 55.7567, 37.6173)
        assert 90 < dist < 110


class TestDistanceMatrix:
    def test_returns_numpy_array(self):
        waypoints = [
            {"lat": 55.75, "lon": 37.61, "alt": 0},
            {"lat": 55.76, "lon": 37.62, "alt": 50},
        ]
        matrix = calculate_distance_matrix(waypoints)
        assert isinstance(matrix, np.ndarray)
    
    def test_matrix_shape(self):
        waypoints = [
            {"lat": 55.75, "lon": 37.61, "alt": 0},
            {"lat": 55.76, "lon": 37.62, "alt": 50},
            {"lat": 55.77, "lon": 37.63, "alt": 100},
        ]
        matrix = calculate_distance_matrix(waypoints)
        assert matrix.shape == (3, 3)
    
    def test_diagonal_is_zero(self):
        waypoints = [
            {"lat": 55.75, "lon": 37.61, "alt": 0},
            {"lat": 55.76, "lon": 37.62, "alt": 50},
        ]
        matrix = calculate_distance_matrix(waypoints)
        assert matrix[0, 0] == 0
        assert matrix[1, 1] == 0
    
    def test_symmetric(self):
        waypoints = [
            {"lat": 55.75, "lon": 37.61, "alt": 0},
            {"lat": 55.76, "lon": 37.62, "alt": 50},
        ]
        matrix = calculate_distance_matrix(waypoints)
        # Расстояния должны быть симметричны
        assert abs(matrix[0, 1] - matrix[1, 0]) < 0.01


class TestRouteDistance:
    def test_simple_route(self):
        matrix = np.array([
            [0, 100, 200],
            [100, 0, 150],
            [200, 150, 0]
        ])
        route = [0, 1, 2]
        dist = route_distance(route, matrix)
        assert dist == 250  # 100 + 150


class TestNearestNeighbor:
    def test_returns_tuple(self):
        matrix = np.array([
            [0, 100, 200],
            [100, 0, 150],
            [200, 150, 0]
        ])
        result = nearest_neighbor(matrix)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_visits_all_points(self):
        matrix = np.array([
            [0, 100, 200],
            [100, 0, 150],
            [200, 150, 0]
        ])
        route, _ = nearest_neighbor(matrix)
        assert len(route) == 3
        assert set(route) == {0, 1, 2}


class TestTwoOpt:
    def test_returns_tuple(self):
        matrix = np.array([
            [0, 100, 200],
            [100, 0, 150],
            [200, 150, 0]
        ])
        route = [0, 1, 2]
        result = two_opt(route, matrix)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_no_worse_than_input(self):
        matrix = np.array([
            [0, 100, 200, 300],
            [100, 0, 150, 250],
            [200, 150, 0, 100],
            [300, 250, 100, 0]
        ])
        route = [0, 1, 2, 3]
        original_dist = route_distance(route, matrix)
        optimized, opt_dist = two_opt(route, matrix)
        assert opt_dist <= original_dist


class TestOptimizeRoute:
    def test_returns_dict(self):
        waypoints = [
            {"id": 1, "lat": 55.75, "lon": 37.61, "alt": 0},
            {"id": 2, "lat": 55.76, "lon": 37.62, "alt": 50},
            {"id": 3, "lat": 55.77, "lon": 37.63, "alt": 100},
        ]
        result = optimize_route(waypoints)
        assert isinstance(result, dict)
    
    def test_contains_required_keys(self):
        waypoints = [
            {"id": 1, "lat": 55.75, "lon": 37.61, "alt": 0},
            {"id": 2, "lat": 55.76, "lon": 37.62, "alt": 50},
        ]
        result = optimize_route(waypoints)
        assert "original_route" in result
        assert "optimized_route" in result
        assert "original_distance" in result
        assert "optimized_distance" in result
        assert "improvement" in result
