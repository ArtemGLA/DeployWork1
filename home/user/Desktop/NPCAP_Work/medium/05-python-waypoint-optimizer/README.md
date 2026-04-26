# Задание 5: Waypoint Optimizer

**Уровень:** Средний  
**Технологии:** Python, numpy  
**Время выполнения:** 4-6 часов

## Описание

Оптимизация маршрута миссии позволяет сократить время полёта и расход батареи. Это вариация задачи коммивояжёра (TSP), где нужно посетить все точки с минимальной общей длиной пути.

## Цель

Реализовать алгоритмы оптимизации маршрута:

1. Жадный алгоритм (Nearest Neighbor)
2. 2-opt оптимизация
3. Генетический алгоритм (опционально)

## Входные данные

Список waypoints с координатами и ограничениями:

```python
waypoints = [
    {"id": 1, "lat": 55.7558, "lon": 37.6173, "alt": 50, "type": "start"},
    {"id": 2, "lat": 55.7600, "lon": 37.6200, "alt": 100, "required_order": None},
    {"id": 3, "lat": 55.7550, "lon": 37.6250, "alt": 75, "required_order": None},
    {"id": 4, "lat": 55.7620, "lon": 37.6150, "alt": 100, "required_order": None},
    {"id": 5, "lat": 55.7580, "lon": 37.6300, "alt": 50, "required_order": None},
    {"id": 6, "lat": 55.7558, "lon": 37.6173, "alt": 0, "type": "end"},
]
```

## Что нужно реализовать

### 1. Расчёт расстояний

```python
def calculate_distance_matrix(waypoints: list[dict]) -> np.ndarray:
    """
    Вычислить матрицу расстояний между всеми парами waypoints.
    
    Учитывать:
    - Горизонтальное расстояние (Haversine)
    - Вертикальное расстояние (разница высот)
    - Общее 3D расстояние
    """
    pass
```

### 2. Жадный алгоритм

```python
def nearest_neighbor(distance_matrix: np.ndarray, 
                     start: int = 0) -> tuple[list[int], float]:
    """
    Жадный алгоритм: на каждом шаге выбирать ближайшую непосещённую точку.
    
    Returns:
        (маршрут, общая длина)
    """
    pass
```

### 3. 2-opt оптимизация

```python
def two_opt(route: list[int], 
            distance_matrix: np.ndarray) -> tuple[list[int], float]:
    """
    2-opt: итеративно улучшать маршрут, 
    меняя местами рёбра если это уменьшает длину.
    
    Алгоритм:
    1. Для каждой пары рёбер (i,i+1) и (j,j+1)
    2. Попробовать заменить на (i,j) и (i+1,j+1)
    3. Если новый маршрут короче - принять
    4. Повторять пока есть улучшения
    """
    pass
```

### 4. Полная оптимизация

```python
def optimize_route(waypoints: list[dict], 
                   method: str = "2opt",
                   constraints: dict = None) -> dict:
    """
    Оптимизировать маршрут с учётом ограничений.
    
    Args:
        waypoints: список точек
        method: "greedy", "2opt", "genetic"
        constraints: ограничения (фиксированные точки, порядок)
        
    Returns:
        {
            "original_route": [...],
            "optimized_route": [...],
            "original_distance": float,
            "optimized_distance": float,
            "improvement": float,  # процент улучшения
        }
    """
    pass
```

### 5. Учёт ограничений

- **Фиксированные точки**: start и end не перемещаются
- **Обязательный порядок**: некоторые точки должны посещаться в определённом порядке
- **Запретные зоны**: маршрут не должен проходить через определённые области

## Примеры

```python
from optimizer import optimize_route, visualize_route

waypoints = [
    {"id": 1, "lat": 55.7558, "lon": 37.6173, "type": "start"},
    {"id": 2, "lat": 55.7600, "lon": 37.6200},
    {"id": 3, "lat": 55.7550, "lon": 37.6250},
    {"id": 4, "lat": 55.7620, "lon": 37.6150},
    {"id": 5, "lat": 55.7580, "lon": 37.6300},
    {"id": 6, "lat": 55.7558, "lon": 37.6173, "type": "end"},
]

result = optimize_route(waypoints, method="2opt")

print(f"Original distance: {result['original_distance']:.1f}m")
print(f"Optimized distance: {result['optimized_distance']:.1f}m")
print(f"Improvement: {result['improvement']:.1f}%")

# Визуализация
visualize_route(waypoints, result['optimized_route'])
```

## Структура проекта

```
src/
├── optimizer.py       # Основные алгоритмы (реализовать)
├── distance.py        # Расчёт расстояний (реализовать)
├── constraints.py     # Обработка ограничений (реализовать)
├── visualize.py       # Визуализация (готово)
└── main.py            # CLI интерфейс
tests/
└── test_optimizer.py  # Тесты
data/
└── missions/          # Тестовые миссии
```

## Запуск

```bash
cd medium/05-python-waypoint-optimizer
pip install -r requirements.txt

# Оптимизация миссии
python src/main.py --mission data/missions/test.json --method 2opt

# Визуализация
python src/main.py --mission data/missions/test.json --visualize
```

## Тестирование

```bash
python -m pytest tests/ -v
```

## Критерии оценки

- [ ] Корректный расчёт расстояний (Haversine)
- [ ] Работающий жадный алгоритм
- [ ] Работающий 2-opt
- [ ] Учёт фиксированных точек start/end
- [ ] Визуализация маршрута
- [ ] Код проходит тесты

## Подсказки

1. Для 2-opt начните с простой версии без ограничений
2. Используйте numpy для эффективных матричных операций
3. Для визуализации используйте matplotlib
4. Тестируйте на маленьких примерах (5-10 точек)

## Дополнительно (необязательно)

- Генетический алгоритм
- Учёт ветра и времени полёта
- Параллельная оптимизация нескольких маршрутов
- Интерактивная визуализация
