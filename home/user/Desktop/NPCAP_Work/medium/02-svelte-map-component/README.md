# Задание 2: Map Component

**Уровень:** Средний  
**Технологии:** Svelte, TypeScript, Leaflet/MapLibre  
**Время выполнения:** 4-6 часов

## Описание

Карта — центральный элемент наземной станции управления БПЛА. Она показывает текущую позицию дрона, траекторию полёта и запланированные waypoints.

В этом задании вам нужно создать интерактивный картографический компонент с отображением траектории в реальном времени.

## Цель

Создать Svelte компонент `DroneMap`, который:

1. Отображает карту с OpenStreetMap тайлами
2. Показывает текущую позицию дрона (маркер)
3. Рисует траекторию движения в реальном времени
4. Отображает waypoints миссии
5. Получает данные через WebSocket

## Макет

```
┌─────────────────────────────────────────────────┐
│  [+] [-]           DRONE MAP                    │
├─────────────────────────────────────────────────┤
│                                                 │
│     ●──────●──────●                            │
│     1      2      3   <- waypoints             │
│                  /                              │
│                 /                               │
│                ▲  <- drone marker              │
│               /                                 │
│     - - - - /      <- trajectory               │
│            ●                                    │
│           HOME                                  │
│                                                 │
├─────────────────────────────────────────────────┤
│  Lat: 55.7565  Lon: 37.6180  Alt: 50m          │
└─────────────────────────────────────────────────┘
```

## Что нужно реализовать

### 1. Компонент DroneMap

```svelte
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { DronePosition, Waypoint, Mission } from './types';
  
  export let center: [number, number] = [55.7558, 37.6173];
  export let zoom: number = 15;
  export let mission: Mission | null = null;
  export let wsUrl: string = 'ws://localhost:8080';
  
  let dronePosition: DronePosition | null = null;
  let trajectory: [number, number][] = [];
</script>

<div class="map-container">
  <!-- Карта Leaflet/MapLibre -->
</div>
```

### 2. Типы данных

```typescript
interface DronePosition {
  lat: number;
  lon: number;
  alt: number;
  heading: number;
  groundspeed: number;
  timestamp: number;
}

interface Waypoint {
  id: number;
  lat: number;
  lon: number;
  alt: number;
  type: 'takeoff' | 'waypoint' | 'land' | 'rtl';
}

interface Mission {
  name: string;
  waypoints: Waypoint[];
}

interface WebSocketMessage {
  type: 'position' | 'mission' | 'status';
  data: DronePosition | Mission | StatusUpdate;
}
```

### 3. WebSocket протокол

Сервер отправляет JSON сообщения:

```json
{
  "type": "position",
  "data": {
    "lat": 55.7565,
    "lon": 37.6180,
    "alt": 50,
    "heading": 90,
    "groundspeed": 10.5,
    "timestamp": 1709640000
  }
}
```

### 4. Требования к UI

1. **Маркер дрона**
   - Вращается согласно heading
   - Меняет цвет: зелёный (норма), жёлтый (предупреждение), красный (ошибка)
   - Показывает направление движения

2. **Траектория**
   - Линия от home до текущей позиции
   - Цвет меняется по высоте (gradient)
   - Последние 1000 точек

3. **Waypoints**
   - Пронумерованные маркеры
   - Линии между waypoints
   - Разные иконки для разных типов (takeoff, waypoint, land)

4. **Контролы**
   - Кнопки zoom
   - Центрирование на дроне
   - Следование за дроном (toggle)

## Структура проекта

```
src/
├── lib/
│   ├── DroneMap.svelte      # Основной компонент (реализовать)
│   ├── DroneMarker.svelte   # Маркер дрона (реализовать)
│   ├── Trajectory.svelte    # Траектория (реализовать)
│   ├── WaypointMarker.svelte # Маркер waypoint (реализовать)
│   ├── types.ts             # Типы (готово)
│   └── websocket.ts         # WebSocket клиент (реализовать)
├── routes/
│   └── +page.svelte         # Демо страница (готово)
└── mock/
    └── server.js            # Mock WebSocket сервер (готово)
```

## Запуск

```bash
cd medium/02-svelte-map-component
npm install

# Запуск mock сервера
node mock/server.cjs &

# Запуск приложения
npm run dev
```

Откройте http://localhost:5173

## Mock сервер

Mock сервер симулирует полёт дрона и отправляет позицию каждые 100мс:

```bash
node mock/server.js --port 8080
```

## Тестирование

```bash
npm run test
```

## Критерии оценки

- [ ] Карта отображается корректно
- [ ] Маркер дрона обновляется в реальном времени
- [ ] Траектория рисуется правильно
- [ ] Waypoints отображаются
- [ ] WebSocket подключение работает
- [ ] Обработка отключения/переподключения
- [ ] Адаптивная вёрстка

## Подсказки

1. Используйте `leaflet` или `maplibre-gl` для карты
2. Для маркера дрона используйте `L.divIcon` с CSS трансформацией
3. Для траектории используйте `L.polyline`
4. WebSocket переподключение с экспоненциальным backoff
5. Используйте Svelte stores для состояния

## Дополнительно (необязательно)

- Кластеризация waypoints при zoom out
- Тепловая карта высоты
- История траекторий (несколько полётов)
- Офлайн тайлы
