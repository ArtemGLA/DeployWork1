/**
 * Drone state store.
 *
 * TODO: Реализуйте store для управления состоянием дронов
 * и подключение к backend через WebSocket.
 */

import { writable, derived } from 'svelte/store';
import type { DroneState, TelemetryUpdate } from '../types';

const API_URL = 'http://localhost:3000';
const WS_URL = 'ws://localhost:3000/ws';

function createDroneStore() {
  const { subscribe, set, update } = writable<Map<number, DroneState>>(new Map());

  let ws: WebSocket | null = null;

  return {
    subscribe,

    /**
     * Подключиться к WebSocket серверу.
     *
     * TODO: Реализуйте подключение
     *
     * Требования:
     * 1. Создать WebSocket соединение
     * 2. Обработать onopen, onmessage, onclose, onerror
     * 3. При получении сообщения типа 'telemetry' — обновить store
     * 4. При отключении — попытаться переподключиться через 3 секунды
     */
    connect: () => {
      // Ваш код здесь
    },

    /**
     * Отключиться от WebSocket.
     *
     * TODO: Реализуйте отключение
     */
    disconnect: () => {
      // Ваш код здесь
    },

    /**
     * Загрузить список дронов через REST API.
     *
     * TODO: Реализуйте fetch
     *
     * Endpoint: GET /api/drones
     */
    fetchAll: async () => {
      // Ваш код здесь
    },

    /**
     * Отправить команду дрону.
     *
     * TODO: Реализуйте отправку команды
     *
     * Endpoint: POST /api/drones/:id/command
     * Body: { command: string, ...params }
     */
    sendCommand: async (droneId: number, command: object) => {
      // Ваш код здесь
      return { success: false, message: 'Not implemented' };
    },
  };
}

export const drones = createDroneStore();

// Текущий выбранный дрон
export const selectedDroneId = writable<number | null>(1);

/**
 * Derived store для получения выбранного дрона.
 *
 * TODO: Реализуйте derived store
 */
export const selectedDrone = derived(
  [drones, selectedDroneId],
  ([$drones, $selectedId]) => {
    // Ваш код здесь
    return null;
  }
);
