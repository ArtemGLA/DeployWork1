# Задание 3: Log Analyzer

**Уровень:** Лёгкий  
**Технологии:** Python, pandas  
**Время выполнения:** 2-3 часа

## Описание

Анализ полётных логов — важная часть работы с БПЛА. Логи помогают выявить проблемы, оптимизировать настройки и расследовать инциденты.

В этом задании вам нужно написать анализатор, который находит аномалии в данных полёта.

## Цель

Реализовать функции в файле `src/analyzer.py`, которые:

1. Загружают CSV файл с данными полёта
2. Находят аномалии в данных
3. Генерируют отчёт об аномалиях

## Типы аномалий

### 1. Резкое изменение высоты
- Изменение более чем на 10 метров за 1 секунду
- Может указывать на турбулентность или ошибку датчика

### 2. Потеря GPS сигнала
- Снижение количества спутников ниже 6
- Изменение fix_type с 3 (3D fix) на 2 или ниже

### 3. Критический уровень батареи
- Напряжение ниже 10.5V (для 3S LiPo)
- Уровень заряда ниже 20%

### 4. Превышение скорости
- Скорость более 20 м/с (72 км/ч) для квадрокоптера
- Может быть опасно для конструкции

### 5. Нестабильное положение
- Резкие изменения roll/pitch (более 0.5 рад за секунду)
- Может указывать на проблемы с калибровкой или ветер

## Формат входных данных

CSV файл `data/flight_log.csv`:

```csv
timestamp,lat,lon,alt,relative_alt,groundspeed,airspeed,heading,roll,pitch,yaw,battery_voltage,battery_remaining,gps_fix,satellites
1709640000,55.755800,37.617300,150.0,0.0,0.0,0.0,0,0.00,0.00,0.00,12.60,100,3,12
...
```

## Что нужно реализовать

```python
def load_flight_log(filepath: str) -> pd.DataFrame:
    """
    Загружает CSV файл с данными полёта.
    
    Returns:
        DataFrame с данными полёта
    """
    pass

def detect_altitude_anomalies(df: pd.DataFrame, threshold: float = 10.0) -> list[dict]:
    """
    Находит резкие изменения высоты.
    
    Returns:
        Список аномалий с timestamp, old_value, new_value, change
    """
    pass

def detect_gps_anomalies(df: pd.DataFrame, min_satellites: int = 6) -> list[dict]:
    """
    Находит потерю GPS сигнала.
    
    Returns:
        Список аномалий с timestamp, satellites, fix_type
    """
    pass

def detect_battery_anomalies(df: pd.DataFrame, 
                             min_voltage: float = 10.5,
                             min_percent: int = 20) -> list[dict]:
    """
    Находит критические уровни батареи.
    """
    pass

def detect_speed_anomalies(df: pd.DataFrame, max_speed: float = 20.0) -> list[dict]:
    """
    Находит превышение скорости.
    """
    pass

def detect_attitude_anomalies(df: pd.DataFrame, max_rate: float = 0.5) -> list[dict]:
    """
    Находит нестабильное положение.
    """
    pass

def generate_report(anomalies: dict) -> str:
    """
    Генерирует текстовый отчёт об аномалиях.
    """
    pass
```

## Пример использования

```python
from analyzer import *

df = load_flight_log('data/flight_log.csv')

anomalies = {
    'altitude': detect_altitude_anomalies(df),
    'gps': detect_gps_anomalies(df),
    'battery': detect_battery_anomalies(df),
    'speed': detect_speed_anomalies(df),
    'attitude': detect_attitude_anomalies(df),
}

report = generate_report(anomalies)
print(report)
```

## Ожидаемый формат отчёта

```
=== FLIGHT LOG ANALYSIS REPORT ===

Total records: 51
Flight duration: 50 seconds

--- ALTITUDE ANOMALIES (2 found) ---
[1709640030] Rapid altitude change: 200.0m -> 185.0m (Δ-15.0m)
[1709640031] Rapid altitude change: 185.0m -> 170.0m (Δ-15.0m)

--- GPS ANOMALIES (1 found) ---
[1709640031] GPS signal degraded: 5 satellites, fix_type=2

--- BATTERY ANOMALIES (0 found) ---
No anomalies detected.

--- SPEED ANOMALIES (0 found) ---
No anomalies detected.

--- ATTITUDE ANOMALIES (1 found) ---
[1709640030] Unstable attitude: roll=-0.15, pitch=0.25

=== END OF REPORT ===
```

## Запуск

```bash
cd easy/03-python-log-analyzer
pip install -r requirements.txt
python src/analyzer.py
```

## Тестирование

```bash
python -m pytest tests/ -v
```

## Критерии оценки

- [ ] Корректная загрузка CSV файла
- [ ] Правильное обнаружение всех типов аномалий
- [ ] Информативный отчёт
- [ ] Код проходит все тесты
- [ ] Использование pandas для обработки данных

## Дополнительно (необязательно)

- Визуализация аномалий на графике (matplotlib)
- Экспорт отчёта в JSON
- Статистический анализ (среднее, медиана, стандартное отклонение)
