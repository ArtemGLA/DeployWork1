# Задание 3: SITL Integration

**Уровень:** Сложный  
**Технологии:** Python, ArduPilot SITL, Docker  
**Время выполнения:** 8-12 часов

## Описание

SITL (Software In The Loop) — это симулятор ArduPilot, который позволяет тестировать прошивки без реального оборудования. В этом задании вам нужно создать автоматизированный тест-сценарий полёта.

## Цель

Создать Python фреймворк для:

1. Запуска SITL через Docker
2. Подключения и управления симулятором
3. Выполнения автоматизированных тестовых сценариев
4. Сбора и анализа результатов

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Framework                           │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │ SITL Manager   │  │ MAVLink Client │  │ Test Runner   │ │
│  │ (Docker)       │  │                │  │               │ │
│  └───────┬────────┘  └───────┬────────┘  └───────┬───────┘ │
│          │                   │                   │         │
└──────────┼───────────────────┼───────────────────┼─────────┘
           │                   │                   │
           ▼                   ▼                   ▼
    ┌──────────────┐   ┌──────────────┐    ┌──────────────┐
    │ SITL Docker  │◀──│  MAVLink     │◀───│ Test Cases   │
    │ Container    │   │  Protocol    │    │              │
    └──────────────┘   └──────────────┘    └──────────────┘
```

## Тестовые сценарии

### 1. Базовый полёт (Simple Flight)
- Взлёт на 20м
- Полёт к waypoint (100м от home)
- Возврат домой
- Посадка

### 2. Миссия с несколькими точками (Multi-waypoint)
- Взлёт
- Пролёт через 5 waypoints
- RTL

### 3. Failsafe тест (Battery Failsafe)
- Взлёт
- Симуляция низкого заряда
- Проверка активации failsafe
- Проверка RTL

### 4. Geofence тест
- Взлёт
- Попытка выйти за geofence
- Проверка ограничения

## Что нужно реализовать

### 1. SITL Manager

```python
class SITLManager:
    """Управление SITL через Docker."""
    
    def __init__(self, vehicle: str = "copter", version: str = "latest"):
        self.vehicle = vehicle
        self.container = None
    
    async def start(self) -> bool:
        """Запустить SITL контейнер."""
        pass
    
    async def stop(self):
        """Остановить контейнер."""
        pass
    
    async def wait_ready(self, timeout: float = 60) -> bool:
        """Ждать готовности SITL."""
        pass
    
    def get_connection_string(self) -> str:
        """Получить строку подключения MAVLink."""
        pass
```

### 2. MAVLink Client

```python
class DroneClient:
    """Клиент управления дроном через MAVLink."""
    
    def __init__(self, connection_string: str):
        self.connection = None
    
    async def connect(self) -> bool:
        """Установить соединение."""
        pass
    
    async def arm(self) -> bool:
        """Армировать дрон."""
        pass
    
    async def takeoff(self, altitude: float) -> bool:
        """Взлёт на заданную высоту."""
        pass
    
    async def goto(self, lat: float, lon: float, alt: float) -> bool:
        """Лететь к точке."""
        pass
    
    async def land(self) -> bool:
        """Посадка."""
        pass
    
    async def rtl(self) -> bool:
        """Return to Launch."""
        pass
    
    async def wait_altitude(self, altitude: float, tolerance: float = 1.0, timeout: float = 30) -> bool:
        """Ждать достижения высоты."""
        pass
    
    async def wait_position(self, lat: float, lon: float, tolerance: float = 5.0, timeout: float = 60) -> bool:
        """Ждать достижения позиции."""
        pass
    
    @property
    def position(self) -> tuple[float, float, float]:
        """Текущая позиция (lat, lon, alt)."""
        pass
    
    @property
    def armed(self) -> bool:
        """Статус армирования."""
        pass
    
    @property
    def mode(self) -> str:
        """Текущий режим."""
        pass
```

### 3. Test Framework

```python
class TestCase:
    """Базовый класс тестового сценария."""
    
    def __init__(self, drone: DroneClient):
        self.drone = drone
        self.results = []
    
    async def setup(self):
        """Подготовка к тесту."""
        pass
    
    async def run(self) -> bool:
        """Выполнение теста."""
        raise NotImplementedError
    
    async def teardown(self):
        """Очистка после теста."""
        pass
    
    def assert_position(self, lat: float, lon: float, tolerance: float = 5.0):
        """Проверка позиции."""
        pass
    
    def assert_altitude(self, alt: float, tolerance: float = 1.0):
        """Проверка высоты."""
        pass

class TestRunner:
    """Запуск тестов."""
    
    def __init__(self, sitl: SITLManager, drone: DroneClient):
        self.sitl = sitl
        self.drone = drone
        self.tests = []
    
    def add_test(self, test: TestCase):
        self.tests.append(test)
    
    async def run_all(self) -> dict:
        """Запустить все тесты."""
        pass
    
    def generate_report(self) -> str:
        """Сгенерировать отчёт."""
        pass
```

## Примеры тестов

```python
class SimpleFlightTest(TestCase):
    """Тест простого полёта."""
    
    async def run(self) -> bool:
        # Армирование
        assert await self.drone.arm(), "Failed to arm"
        
        # Взлёт
        assert await self.drone.takeoff(20), "Failed to takeoff"
        assert await self.drone.wait_altitude(20, timeout=30), "Failed to reach altitude"
        
        # Полёт к точке
        target_lat = self.drone.position[0] + 0.001  # ~100м на север
        target_lon = self.drone.position[1]
        assert await self.drone.goto(target_lat, target_lon, 20), "Failed to start goto"
        assert await self.drone.wait_position(target_lat, target_lon), "Failed to reach position"
        
        # RTL
        assert await self.drone.rtl(), "Failed to start RTL"
        
        # Ждать посадки
        await asyncio.sleep(30)
        assert not self.drone.armed, "Should be disarmed after landing"
        
        return True
```

## Docker

### docker-compose.yml

```yaml
version: '3'
services:
  sitl:
    image: ardupilot/sitl-copter:latest
    ports:
      - "5760:5760"  # MAVLink
      - "5501:5501"  # SITL output
    environment:
      - VEHICLE=ArduCopter
```

### Запуск вручную

```bash
docker run -it --rm \
  -p 5760:5760 \
  ardupilot/sitl-copter:latest
```

## Структура проекта

```
src/
├── sitl_manager.py    # Управление SITL
├── drone_client.py    # MAVLink клиент
├── test_framework.py  # Тестовый фреймворк
├── test_cases/
│   ├── simple_flight.py
│   ├── multi_waypoint.py
│   ├── failsafe.py
│   └── geofence.py
└── main.py            # CLI
tests/
└── test_integration.py
docker/
├── docker-compose.yml
└── Dockerfile
```

## Запуск

```bash
cd hard/03-python-sitl-integration
pip install -r requirements.txt

# Запуск SITL
docker-compose up -d

# Запуск тестов
python src/main.py --test simple_flight

# Все тесты
python src/main.py --all

# С отчётом
python src/main.py --all --report report.html
```

## Критерии оценки

- [ ] Запуск SITL через Docker
- [ ] Подключение MAVLink
- [ ] Базовые команды (arm, takeoff, goto, land)
- [ ] Ожидание условий (altitude, position)
- [ ] Минимум 2 тестовых сценария
- [ ] Генерация отчёта
- [ ] Обработка ошибок и timeout

## Подсказки

1. Используйте `pymavlink` для MAVLink
2. `docker` Python SDK для управления контейнерами
3. Начните с простого теста arm/disarm
4. SITL требует времени на инициализацию (~30 сек)
5. Используйте `asyncio` для асинхронности

## Дополнительно (необязательно)

- Параллельный запуск нескольких SITL
- Тестирование разных прошивок (Plane, Rover)
- CI/CD интеграция (GitHub Actions)
- Визуализация траектории теста
