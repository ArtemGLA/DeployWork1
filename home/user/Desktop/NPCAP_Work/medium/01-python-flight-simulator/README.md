# Задание 1: Flight Simulator

**Уровень:** Средний  
**Технологии:** Python, asyncio  
**Время выполнения:** 4-6 часов

## Описание

Симулятор полёта эмулирует движение дрона между waypoints. Он используется для тестирования наземных станций и алгоритмов планирования миссий без реального оборудования.

В этом задании вам нужно реализовать логику движения дрона с отправкой телеметрии по MAVLink.

## Цель

Создать асинхронный симулятор, который:

1. Загружает миссию из JSON файла
2. Симулирует движение между waypoints
3. Отправляет MAVLink телеметрию по UDP
4. Поддерживает команды управления (arm, disarm, start, pause)

## Архитектура

```
┌──────────────────┐     ┌──────────────────┐
│   Mission File   │────▶│  FlightSimulator │
│   (JSON)         │     │                  │
└──────────────────┘     │  ┌────────────┐  │
                         │  │ DroneState │  │
┌──────────────────┐     │  └────────────┘  │
│ Command Handler  │────▶│                  │
│   (UDP:14551)    │     │  ┌────────────┐  │
└──────────────────┘     │  │ Physics    │  │
                         │  └────────────┘  │
                         │         │        │
                         │         ▼        │
                         │  ┌────────────┐  │
                         │  │ MAVLink TX │──┼──▶ UDP:14550
                         │  └────────────┘  │
                         └──────────────────┘
```

## Физическая модель

### Параметры движения
- Максимальная скорость: 15 м/с
- Ускорение: 2 м/с²
- Скорость подъёма/спуска: 3 м/с
- Радиус захвата waypoint: 5 м

### Расчёт движения

На каждом шаге симуляции (dt = 0.1с):

1. Вычислить направление к текущему waypoint
2. Вычислить желаемую скорость (с учётом ускорения)
3. Обновить позицию: pos += velocity * dt
4. Проверить достижение waypoint
5. Перейти к следующему waypoint если достигнут

## Что нужно реализовать

### Основной класс `FlightSimulator`

```python
class FlightSimulator:
    def __init__(self, system_id: int = 1):
        self.state = DroneState()
        self.mission: list[Waypoint] = []
        self.current_wp: int = 0
        self.running: bool = False
        
    async def load_mission(self, filepath: str) -> bool:
        """Загрузить миссию из JSON файла."""
        pass
    
    async def run(self, telemetry_port: int = 14550, command_port: int = 14551):
        """Запустить симулятор."""
        pass
    
    def arm(self) -> bool:
        """Армировать дрон."""
        pass
    
    def disarm(self) -> bool:
        """Дизармировать дрон."""
        pass
    
    def start_mission(self) -> bool:
        """Начать выполнение миссии."""
        pass
    
    def pause_mission(self):
        """Приостановить миссию."""
        pass
    
    def update_physics(self, dt: float):
        """Обновить физику движения."""
        pass
```

### Класс состояния `DroneState`

```python
@dataclass
class DroneState:
    lat: float = 0.0
    lon: float = 0.0
    alt: float = 0.0
    
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
    
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    
    battery: float = 100.0
    armed: bool = False
    mode: str = "STABILIZE"
```

### Формат миссии

```json
{
  "name": "Test Mission",
  "home": {
    "lat": 55.7558,
    "lon": 37.6173,
    "alt": 0
  },
  "waypoints": [
    {"lat": 55.7565, "lon": 37.6180, "alt": 50, "speed": 10},
    {"lat": 55.7575, "lon": 37.6190, "alt": 100, "speed": 15},
    {"lat": 55.7570, "lon": 37.6170, "alt": 50, "speed": 10}
  ],
  "settings": {
    "takeoff_alt": 20,
    "rtl_alt": 30
  }
}
```

## Команды управления

Симулятор принимает JSON команды по UDP:

```json
{"command": "arm"}
{"command": "disarm"}
{"command": "start"}
{"command": "pause"}
{"command": "goto", "lat": 55.7570, "lon": 37.6180, "alt": 50}
{"command": "rtl"}
{"command": "land"}
```

## Запуск

```bash
cd medium/01-python-flight-simulator
pip install -r requirements.txt

# Запуск симулятора с миссией
python src/simulator.py --mission data/mission.json

# В другом терминале - отправка команд
python src/commander.py arm
python src/commander.py start
```

## Тестирование

```bash
python -m pytest tests/ -v
```

## Визуализация (опционально)

Для отладки можно использовать скрипт визуализации:

```bash
python src/visualize.py  # Показывает траекторию в реальном времени
```

## Критерии оценки

- [ ] Корректная загрузка миссии
- [ ] Плавное движение между waypoints
- [ ] Отправка MAVLink телеметрии
- [ ] Обработка команд управления
- [ ] Асинхронная архитектура
- [ ] Код проходит все тесты

## Подсказки

1. Используйте `asyncio.create_task()` для параллельных задач
2. Для UDP используйте `asyncio.DatagramProtocol`
3. Разряд батареи: ~0.1% в секунду при полёте
4. Используйте формулы из задания 04 (Coordinate Converter) для расчёта расстояний

## Дополнительно (необязательно)

- Учёт ветра (добавление случайного смещения)
- RTL (Return To Launch) логика
- Failsafe режимы (низкая батарея, потеря связи)
