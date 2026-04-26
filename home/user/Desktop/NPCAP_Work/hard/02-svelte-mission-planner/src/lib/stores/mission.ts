/**
 * Mission Store - управление состоянием миссии.
 *
 * TODO: Реализуйте store и функции управления миссией.
 */

import { writable, derived, get } from 'svelte/store';
import type { Mission, Waypoint, MissionStats, HomePosition } from '../types';

function generateId(): string {
  return Math.random().toString(36).substring(2, 9);
}

function createEmptyMission(): Mission {
  return {
    id: generateId(),
    name: 'New Mission',
    home: { lat: 55.7558, lon: 37.6173, alt: 150 },
    waypoints: [],
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
}

function createMissionStore() {
  const { subscribe, set, update } = writable<Mission>(createEmptyMission());

  return {
    subscribe,

    /**
     * Создать новую пустую миссию.
     */
    reset: () => {
      set(createEmptyMission());
    },

    /**
     * Загрузить миссию.
     */
    load: (mission: Mission) => {
      set(mission);
    },

    /**
     * Установить home позицию.
     *
     * TODO: Реализуйте установку home
     */
    setHome: (home: HomePosition) => {
      // Ваш код здесь
    },

    /**
     * Добавить waypoint.
     *
     * TODO: Реализуйте добавление waypoint
     *
     * Требования:
     * 1. Создать объект Waypoint с уникальным id
     * 2. Добавить в массив waypoints
     * 3. Обновить updatedAt
     */
    addWaypoint: (
      lat: number,
      lon: number,
      alt: number,
      type: Waypoint['type'] = 'waypoint'
    ) => {
      // Ваш код здесь
    },

    /**
     * Удалить waypoint по id.
     *
     * TODO: Реализуйте удаление waypoint
     */
    removeWaypoint: (id: string) => {
      // Ваш код здесь
    },

    /**
     * Обновить waypoint.
     *
     * TODO: Реализуйте обновление waypoint
     */
    updateWaypoint: (id: string, updates: Partial<Waypoint>) => {
      // Ваш код здесь
    },

    /**
     * Переместить waypoint в списке.
     *
     * TODO: Реализуйте перемещение
     *
     * Подсказка: используйте splice для удаления и вставки элемента
     */
    moveWaypoint: (fromIndex: number, toIndex: number) => {
      // Ваш код здесь
    },

    /**
     * Добавить waypoint после определённого.
     *
     * TODO: Реализуйте вставку после указанного waypoint
     */
    insertWaypointAfter: (afterId: string, lat: number, lon: number, alt: number) => {
      // Ваш код здесь
    },
  };
}

export const mission = createMissionStore();

/**
 * Вычисление статистики миссии.
 *
 * TODO: Реализуйте derived store для статистики
 *
 * Требования:
 * - waypointCount: количество waypoints
 * - totalDistance: суммарное расстояние между точками (Haversine)
 * - estimatedTime: оценочное время полёта (distance / avg_speed)
 * - maxAltitude: максимальная высота
 * - minAltitude: минимальная высота
 */
export const missionStats = derived(mission, ($mission): MissionStats => {
  // Ваш код здесь

  return {
    waypointCount: 0,
    totalDistance: 0,
    estimatedTime: 0,
    maxAltitude: 0,
    minAltitude: 0,
  };
});

/**
 * Сохранение в localStorage.
 *
 * TODO: Реализуйте сохранение
 */
export function saveMissionToStorage(): void {
  // Ваш код здесь
}

/**
 * Загрузка из localStorage.
 *
 * TODO: Реализуйте загрузку
 */
export function loadMissionFromStorage(): boolean {
  // Ваш код здесь
  return false;
}

// Вспомогательные функции для экспорта
export function newMission(): void {
  mission.reset();
}

export function addWaypoint(data: { lat: number; lon: number; alt: number; type?: number }): void {
  const type = data.type === 22 ? 'takeoff' : data.type === 21 ? 'land' : 'waypoint';
  mission.addWaypoint(data.lat, data.lon, data.alt, type);
}

export function removeWaypoint(id: string): void {
  mission.removeWaypoint(id);
}

export function updateWaypoint(id: string, updates: Partial<Waypoint>): void {
  mission.updateWaypoint(id, updates);
}

export function moveWaypoint(fromIndex: number, toIndex: number): void {
  mission.moveWaypoint(fromIndex, toIndex);
}
