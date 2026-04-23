"""
Waypoint Optimizer - оптимизация маршрута миссии.

Задание: реализуйте алгоритмы оптимизации маршрута.
"""

import math
import numpy as np
from typing import Optional


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние между точками в метрах (формула Хаверсина)."""
    R = 6371000  # радиус Земли в метрах
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def calculate_distance_matrix(waypoints: list[dict]) -> np.ndarray:
    """
    Вычислить матрицу расстояний между всеми парами waypoints.
    
    Args:
        waypoints: список точек с lat, lon, alt
        
    Returns:
        numpy матрица NxN с расстояниями
    """
    n = len(waypoints)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j:
                # horizontal = haversine_distance(lat1, lon1, lat2, lon2)
                horizontal = haversine_distance(waypoints[i]['lat'], waypoints[i]['lon'], 
                                                  waypoints[j]['lat'], waypoints[j]['lon'])
                # vertical = abs(alt1 - alt2)
                vertical = abs (waypoints[i]['alt'] - waypoints[j]['alt'])

                # matrix = sqrt(horizontal^2 + vertical^2)
                matrix[i, j] = math.sqrt(horizontal**2 + vertical**2)
    
    return matrix


def route_distance(route: list[int], distance_matrix: np.ndarray) -> float:
    """Вычислить общую длину маршрута."""
    total = 0.0
    for i in range(len(route) - 1):
        total += distance_matrix[route[i], route[i + 1]]
    return total


def nearest_neighbor(distance_matrix: np.ndarray, 
                     start: int = 0,
                     end: Optional[int] = None) -> tuple[list[int], float]:
    """
    Жадный алгоритм ближайшего соседа.
    
    TODO: Реализуйте алгоритм
    
    Алгоритм:
    1. Начать с точки start
    2. На каждом шаге выбирать ближайшую непосещённую точку
    3. Повторять пока все точки не посещены
    4. Если задан end - закончить в этой точке
    
    Args:
        distance_matrix: матрица расстояний NxN
        start: индекс начальной точки
        end: индекс конечной точки (если отличается от start)
        
    Returns:
        (route, total_distance)
    """
    n = distance_matrix.shape[0]
    visited = [False] * n
    route = [start]
    visited[start] = True
    
    if end is not None:
        visited[end] = True  # Зарезервировать конечную точку

    current = start
    while len(route) < n - (1 if end is not None else 0):

        nearest = None
        nearest_dist = float('inf')
        for j in range(n):
            if not visited[j] and distance_matrix[current, j] < nearest_dist:
                nearest = j
                nearest_dist = distance_matrix[current, j]
        route.append(nearest)
        visited[nearest] = True
        current = nearest
    
    if end is not None:
        route.append(end)
    
    total = route_distance(route, distance_matrix)
    return route, total


def two_opt(route: list[int], 
            distance_matrix: np.ndarray,
            max_iterations: int = 1000) -> tuple[list[int], float]:
    """
    2-opt оптимизация маршрута.
    
    TODO: Реализуйте алгоритм
    
    Алгоритм:
    1. Для каждой пары рёбер (i, i+1) и (j, j+1) где j > i+1
    2. Попробовать "перевернуть" сегмент между i+1 и j
    3. Если новый маршрут короче - принять изменение
    4. Повторять пока есть улучшения
    
    "Переворот" сегмента:
    [a, b, c, d, e, f] с i=1, j=4 даёт [a, b, e, d, c, f]
    
    Args:
        route: начальный маршрут
        distance_matrix: матрица расстояний
        max_iterations: максимум итераций
        
    Returns:
        (optimized_route, total_distance)
    """
    route = route.copy()
    n = len(route)
    improved = True
    iteration = 0
    
    # TODO: Реализуйте 2-opt
    #
    # while improved and iteration < max_iterations:
    #     improved = False
    #     iteration += 1
    #     
    #     for i in range(n - 2):
    #         for j in range(i + 2, n - 1):
    #             # Вычислить изменение длины при перевороте
    #             # delta = new_edges - old_edges
    #             # Если delta < 0 - принять изменение
    #             ...
    
    # Ваш код здесь
    
    total = route_distance(route, distance_matrix)
    return route, total


def optimize_route(waypoints: list[dict], 
                   method: str = "2opt",
                   fixed_start: bool = True,
                   fixed_end: bool = True) -> dict:
    """
    Оптимизировать маршрут миссии.
    
    TODO: Реализуйте функцию оптимизации
    
    Args:
        waypoints: список waypoints с lat, lon, alt
        method: "greedy", "2opt"
        fixed_start: первая точка фиксирована
        fixed_end: последняя точка фиксирована
        
    Returns:
        {
            "original_route": [id1, id2, ...],
            "optimized_route": [id1, id3, id2, ...],
            "original_distance": float,
            "optimized_distance": float,
            "improvement": float,
        }
    """
    n = len(waypoints)
    
    # Оригинальный маршрут
    original_route = list(range(n))
    
    # Матрица расстояний
    distance_matrix = calculate_distance_matrix(waypoints)
    
    # Оригинальная длина
    original_distance = route_distance(original_route, distance_matrix)
    
    # TODO: Оптимизация
    #
    if method == "greedy":
        optimized_route, optimized_distance = nearest_neighbor(distance_matrix)
    # elif method == "2opt":
    #     initial_route, _ = nearest_neighbor(...)
    #     optimized_route, optimized_distance = two_opt(initial_route, ...)
    
    # Ваш код здесь
    
    # Вычисление улучшения
    improvement = (original_distance - optimized_distance) / original_distance * 100
    
    # Конвертация индексов в ID
    original_ids = [waypoints[i].get('id', i) for i in original_route]
    optimized_ids = [waypoints[i].get('id', i) for i in optimized_route]
    
    return {
        "original_route": original_ids,
        "optimized_route": optimized_ids,
        "original_distance": original_distance,
        "optimized_distance": optimized_distance,
        "improvement": improvement,
    }


def main():
    """Пример использования."""
    waypoints = [
        {"id": 1, "lat": 55.7558, "lon": 37.6173, "alt": 0, "type": "start"},
        {"id": 2, "lat": 55.7600, "lon": 37.6200, "alt": 50},
        {"id": 3, "lat": 55.7550, "lon": 37.6250, "alt": 75},
        {"id": 4, "lat": 55.7620, "lon": 37.6150, "alt": 100},
        {"id": 5, "lat": 55.7580, "lon": 37.6300, "alt": 50},
        {"id": 6, "lat": 55.7558, "lon": 37.6173, "alt": 0, "type": "end"},
    ]
    
    result = optimize_route(waypoints, method="2opt")
    
    print("Waypoint Optimizer")
    print("=" * 40)
    print(f"Original route: {result['original_route']}")
    print(f"Optimized route: {result['optimized_route']}")
    print(f"Original distance: {result['original_distance']:.1f} m")
    print(f"Optimized distance: {result['optimized_distance']:.1f} m")
    print(f"Improvement: {result['improvement']:.1f}%")


if __name__ == '__main__':
    main()
