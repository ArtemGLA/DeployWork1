"""
Flight Log Analyzer - анализатор полётных логов для обнаружения аномалий.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import json
matplotlib.use('Qt5Agg')
import numpy as np
from typing import Any, Dict, List, Optional


def load_flight_log(filepath: str) -> pd.DataFrame:
    """
    Загружает CSV файл с данными полёта.
    
    Args:
        filepath: путь к CSV файлу
        
    Returns:
        DataFrame с колонками: timestamp, lat, lon, alt, relative_alt,
        groundspeed, airspeed, heading, roll, pitch, yaw,
        battery_voltage, battery_remaining, gps_fix, satellites
    """

    # Парсинг csv таблицы
    df = pd.read_csv(filepath)
    return df



def detect_altitude_anomalies(df: pd.DataFrame, threshold: float = 10.0) -> List[Dict]:
    """
    Находит резкие изменения высоты.
    
    Аномалия: изменение relative_alt более чем на threshold метров
    за 1 секунду (между соседними записями).
    
    Args:
        df: DataFrame с данными полёта
        threshold: порог изменения высоты в метрах
        
    Returns:
        Список словарей с полями:
        - timestamp: время аномалии
        - old_value: предыдущее значение высоты
        - new_value: новое значение высоты
        - change: величина изменения
    """
    anomalies = []
    
    # Вычисление разницы высот между соседними записями
    alt_diff = df['relative_alt'].diff()
    
    # Нахождение строк с превышением разницы высоты
    anomaly_indices = np.where(abs(alt_diff) > threshold)[0]
    
    # Создание словаря
    # Время, высота прошлого положения, высота настоящего положения, разница высот
    for idx in anomaly_indices:

        anomaly = {
            'timestamp': df.iloc[idx]['timestamp'],
            'old_value': df.iloc[idx-1]['relative_alt'],
            'new_value': df.iloc[idx]['relative_alt'],
            'change': alt_diff.iloc[idx]
        }
        anomalies.append(anomaly)
    
    return anomalies


def detect_gps_anomalies(df: pd.DataFrame, min_satellites: int = 6) -> List[Dict]:
    """
    Находит потерю GPS сигнала.
    
    Аномалия: количество спутников < min_satellites ИЛИ gps_fix < 3
    
    Args:
        df: DataFrame с данными полёта
        min_satellites: минимальное количество спутников
        
    Returns:
        Список словарей с полями:
        - timestamp: время аномалии
        - satellites: количество спутников
        - fix_type: тип фиксации GPS
    """
    anomalies = []
    
    # Строки с недостаточным количеством спутников или с недостаточной точностью сигналов
    anomaly_mask = (df['satellites'] < min_satellites) | (df['gps_fix'] < 3)
    anomaly_indices = df[anomaly_mask].index

    # Создание словаря
    # Время, высота прошлого положения, высота настоящего положения, разница высот
    for idx in anomaly_indices:
        anomaly = {
            'timestamp': df.loc[idx, 'timestamp'],
            'satellites': df.loc[idx, 'satellites'],
            'fix_type': df.loc[idx, 'gps_fix']
        }
        anomalies.append(anomaly)
    
    return anomalies


def detect_battery_anomalies(df: pd.DataFrame,
                             min_voltage: float = 10.5,
                             min_percent: int = 20) -> List[Dict]:
    """
    Находит критические уровни батареи.
    
    Аномалия: voltage < min_voltage ИЛИ remaining < min_percent
    
    Args:
        df: DataFrame с данными полёта
        min_voltage: минимальное напряжение в вольтах
        min_percent: минимальный уровень заряда в %
        
    Returns:
        Список словарей с полями:
        - timestamp: время аномалии
        - voltage: напряжение
        - remaining: уровень заряда в %
        - reason: причина ('low_voltage' или 'low_charge')
    """
    anomalies = []
    
    # Фильтр недостаточно напряжения, заряда
    anomaly_mask_voltage = df['battery_voltage'] < min_voltage
    anomaly_mask_remaining = df['battery_remaining'] < min_percent
    
    # Создание словаря
    # Время, напряжение, заряд, причина аномалии низкое напряжение
    for row in df[anomaly_mask_voltage].to_dict('records'):
        anomalies.append({
            'timestamp': row['timestamp'],
            'voltage': row['battery_voltage'],
            'remaining': row['battery_remaining'],
            'reason': 'low_voltage'
        })

    # Создание словаря
    # Время, напряжение, заряд, причина аномалии низкий заряд
    for row in df[anomaly_mask_remaining].to_dict('records'):
        anomalies.append({
            'timestamp': row['timestamp'],
            'voltage': row['battery_voltage'],
            'remaining': row['battery_remaining'],
            'reason': 'low_charge'
        })
    
    return anomalies


def detect_speed_anomalies(df: pd.DataFrame, max_speed: float = 20.0) -> List[Dict]:
    """
    Находит превышение скорости.
    
    Аномалия: groundspeed > max_speed
    
    Args:
        df: DataFrame с данными полёта
        max_speed: максимальная скорость в м/с
        
    Returns:
        Список словарей с полями:
        - timestamp: время аномалии
        - speed: скорость в м/с
    """
    anomalies = []
    
    # Фильтр скорость выше максимальной допустимой
    anomaly_mask = df['groundspeed'] > max_speed
    
    # Создание словаря
    # Время, скорость
    for row in df[anomaly_mask].to_dict('records'):
        anomalies.append({
            'timestamp': row['timestamp'],
            'speed': row['groundspeed']
        })
    
    return anomalies


def detect_attitude_anomalies(df: pd.DataFrame, max_rate: float = 0.5) -> List[Dict]:
    """
    Находит нестабильное положение.
    
    Аномалия: резкое изменение roll или pitch (более max_rate рад за секунду)
    
    Args:
        df: DataFrame с данными полёта
        max_rate: максимальная скорость изменения угла в рад/с
        
    Returns:
        Список словарей с полями:
        - timestamp: время аномалии
        - roll: значение крена
        - pitch: значение тангажа
        - roll_rate: скорость изменения крена
        - pitch_rate: скорость изменения тангажа
    """
    anomalies = []
    
    # Вычисление изменения крена и тангажа
    roll_rate = df['roll'].diff().abs()
    pitch_rate = df['pitch'].diff().abs()
    
    # Фильтр изменения тангажа и крена выше максимальной допустимой
    anomaly_indices = np.where((roll_rate > max_rate) | (pitch_rate > max_rate))[0]
    
    # Создание словаря
    # Время, тангаж, крен, изменение тангажа, изменение крена
    for idx in anomaly_indices:
        if idx > 0 and idx < len(df):
            anomaly = {
                'timestamp': df.iloc[idx]['timestamp'],
                'roll': df.iloc[idx]['roll'],
                'pitch': df.iloc[idx]['pitch'],
                'roll_rate': roll_rate.iloc[idx],
                'pitch_rate': pitch_rate.iloc[idx]
            }
            anomalies.append(anomaly)
    
    return anomalies


def generate_report(anomalies: Dict[str, List[Dict]], 
                    df: Optional[pd.DataFrame] = None) -> str:
    """
    Генерирует текстовый отчёт об аномалиях.
    
    Args:
        anomalies: словарь с аномалиями по категориям
        df: DataFrame для дополнительной статистики
        
    Returns:
        Строка с отформатированным отчётом
    """
    lines = ["=== FLIGHT LOG ANALYSIS REPORT ===", ""]
    
    # Длительность полета
    if df is not None:
        duration = df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]
        lines.append(f"Flight duration: {duration} seconds \n")
    
    # Категории аномалий в нужном порядке
    categories = [
        ('altitude', 'ALTITUDE ANOMALIES'),
        ('gps', 'GPS ANOMALIES'),
        ('battery', 'BATTERY ANOMALIES'),
        ('speed', 'SPEED ANOMALIES'),
        ('attitude', 'ATTITUDE ANOMALIES')
    ]
    
    # Перебор категорий аномалий и вывод их параметров
    # Формирование списка строк
    for key, title in categories:
        anomaly_list = anomalies.get(key, [])
        count = len(anomaly_list)
        
        lines.append(f"--- {title} ({count} found) ---")
        
        if count == 0:
            lines.append("No anomalies detected.")
        else:
            for anomaly in anomaly_list:
                timestamp = anomaly.get('timestamp', 'N/A')
                
                # Высота
                if key == 'altitude':
                    lines.append(
                        f"[{timestamp}] Rapid altitude change: "
                        f"{anomaly['old_value']:.1f}m -> {anomaly['new_value']:.1f}m "
                        f"(Δ{anomaly['change']:.1f}m)"
                    )
                
                # Сигнал
                elif key == 'gps':
                    lines.append(
                        f"[{timestamp}] GPS signal degraded: "
                        f"{anomaly['satellites']} satellites, fix_type={anomaly['fix_type']}"
                    )
                
                # Батарея
                elif key == 'battery':
                    reason_text = "Low voltage" if anomaly['reason'] == 'low_voltage' else "Low charge"
                    lines.append(
                        f"[{timestamp}] Battery {reason_text}: "
                        f"{anomaly['voltage']:.2f}V, {anomaly['remaining']}%"
                    )
                
                # Скорость
                elif key == 'speed':
                    lines.append(
                        f"[{timestamp}] Speed exceeded: {anomaly['speed']:.1f} m/s"
                    )
                
                # Наклон
                elif key == 'attitude':
                    lines.append(
                        f"[{timestamp}] Unstable attitude: "
                        f"roll={anomaly['roll']:.2f}, pitch={anomaly['pitch']:.2f} "
                        f"(Δroll={anomaly['roll_rate']:.2f}, Δpitch={anomaly['pitch_rate']:.2f})"
                    )
        
        lines.append("")

    if df is not None:
        params = ['relative_alt', 'groundspeed', 'battery_voltage', 'battery_remaining', 'satellites', 'roll', 'pitch']
        lines.append("\n=== СТАТИСТИЧЕСКИЙ АНАЛИЗ ===")
        lines.append(f"{'Параметр':<20} {'Среднее':>10} {'Медиана':>10} {'Отклонение':>15}")
        lines.append("-" * 60)
        
        for param in params:
            if param in df.columns:
                mean_val = df[param].mean()
                median_val = df[param].median()
                std_val = df[param].std()
                lines.append(f"{param:<20} {mean_val:>10.2f} {median_val:>10.2f} {std_val:>15.2f}")

        lines.append("=== END OF REPORT ===")
    
    return "\n".join(lines)

def save_to_json(anomalies: Dict[str, List[Dict]], df: pd.DataFrame, filename: str) -> None:
    """
    Сохраняет отчёт об аномалиях и статистику в JSON файл..
    
    Args:
        anomalies: словарь с аномалиями по категориям
        df: DataFrame
        filename: название JSON файла
        
    Returns:
        None
    """
    def convert_to_native(obj):
        """Рекурсивно конвертирует numpy типы в Python native."""
        if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(item) for item in obj]
        else:
            return obj
    
    # Параметры для статистики
    params = ['relative_alt', 'groundspeed', 'battery_voltage', 'battery_remaining', 'satellites', 'roll', 'pitch']
    
    # Сбор статистики
    statistics = {}
    for param in params:
        if param in df.columns:
            statistics[param] = {
                'mean': float(df[param].mean()),
                'median': float(df[param].median()),
                'std': float(df[param].std()),
                'min': float(df[param].min()),
                'max': float(df[param].max())
            }
    
    # Формирование JSON
    report = {
        'total_records': int(len(df)),
        'flight_duration_seconds': float(df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]),
        'statistics': statistics,
        'anomalies': {
            'altitude': anomalies['altitude'],
            'gps': anomalies['gps'],
            'battery': anomalies['battery'],
            'speed': anomalies['speed'],
            'attitude': anomalies['attitude']
        },
        'anomaly_counts': {
            'altitude': len(anomalies['altitude']),
            'gps': len(anomalies['gps']),
            'battery': len(anomalies['battery']),
            'speed': len(anomalies['speed']),
            'attitude': len(anomalies['attitude'])
        }
    }
    
    # Конвертация из numpy типов в обычные Python
    report = convert_to_native(report)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f" Отчёт сохранён в файл: {filename}")
    

def plot_anomalies(df: pd.DataFrame, anomalies: Dict[str, List[Dict]]) -> None:
    """
    Построение графика аномалий
    
    Args:
        df: DataFrame
        anomalies: словарь аномалий
        
    Returns:
        None
    """

    # Создаём массив для индикаторов
    n = len(df)
    time_seconds = (df['timestamp'] - df['timestamp'].iloc[0]).values
    
    # Создаём индикаторы для каждого типа аномалий
    indicators = {
        'altitude': np.zeros(n),
        'gps': np.zeros(n),
        'battery': np.zeros(n),
        'speed': np.zeros(n),
        'attitude': np.zeros(n)
    }
    
    # Отмечаем аномалии
    for anomaly in anomalies['altitude']:
        idx = df[df['timestamp'] == anomaly['timestamp']].index[0]
        indicators['altitude'][idx] = 1
    
    for anomaly in anomalies['gps']:
        idx = df[df['timestamp'] == anomaly['timestamp']].index[0]
        indicators['gps'][idx] = 1
    
    for anomaly in anomalies['battery']:
        idx = df[df['timestamp'] == anomaly['timestamp']].index[0]
        indicators['battery'][idx] = 1
    
    for anomaly in anomalies['speed']:
        idx = df[df['timestamp'] == anomaly['timestamp']].index[0]
        indicators['speed'][idx] = 1
    
    for anomaly in anomalies['attitude']:
        idx = df[df['timestamp'] == anomaly['timestamp']].index[0]
        indicators['attitude'][idx] = 1
    
    # Создаём график
    fig, ax = plt.subplots(figsize=(12, 3))
    
    # Собираем все индикаторы в матрицу
    matrix = np.array([
        indicators['altitude'],
        indicators['gps'],
        indicators['battery'],
        indicators['speed'],
        indicators['attitude']
    ])
    
    # Рисуем цветную карту
    im = ax.imshow(matrix, aspect='auto', cmap='RdYlGn_r', 
                   extent=[time_seconds[0], time_seconds[-1], -0.5, 4.5])
    
    # Настройки
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.set_yticklabels(['Наклон', 'Скорость', 'Батарея', 'GPS', 'Высота'])
    ax.set_xlabel('Индекс')
    ax.set_title('Аномалии полёта')
    
    # Цветовая шкала
    cbar = plt.colorbar(im, ticks=[0, 1])
    cbar.set_ticklabels(['Норма', 'Аномалия'])
    
    plt.tight_layout()
    plt.show()

def main():
    """Пример использования анализатора."""
    import os
    
    # Путь к тестовому файлу
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    log_file = os.path.join(data_dir, 'flight_log.csv')
    
    if not os.path.exists(log_file):
        print(f"Файл {log_file} не найден")
        print("Скопируйте flight_log.csv из common/test-data/")
        return
    
    # Загрузка данных
    df = load_flight_log(log_file)
    
    if df is None:
        print("Ошибка загрузки данных")
        return
    
    print(f"Загружено записей: {len(df)}")
    
    # Обнаружение аномалий
    anomalies = {
        'altitude': detect_altitude_anomalies(df),
        'gps': detect_gps_anomalies(df),
        'battery': detect_battery_anomalies(df),
        'speed': detect_speed_anomalies(df),
        'attitude': detect_attitude_anomalies(df),
    }
    
    # Генерация отчёта
    report = generate_report(anomalies, df)
    print(report)

    # Дополнительные задания
    # Сохранение JSON
    save_to_json(anomalies, df, 'flight_report.json')

    # Построение графика
    plot_anomalies(df, anomalies)

if __name__ == '__main__':
    main()
