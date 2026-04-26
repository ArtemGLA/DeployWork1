/**
 * Валидация миссии.
 *
 * TODO: Реализуйте проверки безопасности миссии.
 */

import type { Mission, ValidationResult, ValidationError } from '../types';

// Лимиты безопасности
const MAX_ALTITUDE = 500; // метров
const MIN_ALTITUDE = 0;
const MAX_SPEED = 20; // м/с
const MAX_DISTANCE_BETWEEN_WAYPOINTS = 5000; // метров
const MAX_TOTAL_DISTANCE = 50000; // метров

/**
 * Валидация миссии.
 *
 * TODO: Реализуйте следующие проверки:
 *
 * 1. Наличие waypoints
 *    - Миссия должна содержать хотя бы один waypoint
 *    - severity: 'error'
 *
 * 2. Первая команда - takeoff
 *    - Первый waypoint должен быть типа 'takeoff'
 *    - severity: 'warning'
 *
 * 3. Последняя команда - land/rtl
 *    - Последний waypoint должен быть 'land' или 'rtl'
 *    - severity: 'warning'
 *
 * 4. Проверка высот
 *    - Все высоты должны быть в диапазоне [MIN_ALTITUDE, MAX_ALTITUDE]
 *    - severity: 'error'
 *
 * 5. Проверка скоростей
 *    - Скорость не должна превышать MAX_SPEED
 *    - severity: 'warning'
 *
 * 6. Проверка координат
 *    - lat должен быть в [-90, 90]
 *    - lon должен быть в [-180, 180]
 *    - severity: 'error'
 *
 * 7. Проверка расстояний между waypoints
 *    - Расстояние между соседними точками не должно превышать MAX_DISTANCE_BETWEEN_WAYPOINTS
 *    - Используйте формулу Haversine
 *    - severity: 'warning'
 *
 * 8. Проверка общей дистанции
 *    - Суммарное расстояние миссии не должно превышать MAX_TOTAL_DISTANCE
 *    - severity: 'warning'
 *
 * @returns ValidationResult с valid=true если нет ошибок уровня 'error'
 */
export function validateMission(mission: Mission): ValidationResult {
  const errors: ValidationError[] = [];

  // TODO: Реализуйте проверки

  // Ваш код здесь

  const hasErrors = errors.some((e) => e.severity === 'error');

  return {
    valid: !hasErrors,
    errors,
  };
}

/**
 * Вычисление расстояния между точками (Haversine).
 *
 * TODO: Реализуйте формулу Haversine
 *
 * @returns расстояние в метрах
 */
function haversineDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  // Ваш код здесь
  return 0;
}
