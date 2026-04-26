# Задание 2: Mission Planner

**Уровень:** Сложный  
**Технологии:** Svelte, TypeScript, Leaflet  
**Время выполнения:** 10-14 часов

## Описание

Mission Planner — полноценный инструмент планирования миссий для БПЛА. Позволяет создавать, редактировать и экспортировать маршруты полёта.

## Функционал

1. **Интерактивная карта** — добавление waypoints кликом
2. **Редактор waypoints** — настройка параметров каждой точки
3. **Типы команд** — takeoff, waypoint, loiter, ROI, land
4. **Редактор высот** — профиль высоты миссии
5. **Валидация** — проверка безопасности маршрута
6. **Экспорт/Импорт** — MAVLink waypoint format, QGroundControl format

## Макет

```
┌─────────────────────────────────────────────────────────────────────────┐
│  File   Edit   View   Tools   Help                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  [New] [Open] [Save] [Export]     |  [Validate] [Optimize] [Upload]    │
├────────────────────────────────────────────────┬────────────────────────┤
│                                                │  Mission Info          │
│                                                │  ────────────────────  │
│         [Interactive Map]                      │  Waypoints: 5          │
│                                                │  Distance: 1.2 km      │
│         ●──────●──────●                       │  Est. time: 8 min      │
│         1      2      3                        │                        │
│                       │                        ├────────────────────────┤
│                       ●                        │  Waypoint Editor       │
│                       4                        │  ────────────────────  │
│                       │                        │  #3 - Waypoint         │
│                       ●                        │  Lat: 55.7565          │
│                       5                        │  Lon: 37.6180          │
│                                                │  Alt: 50m              │
│                                                │  Speed: 10 m/s         │
├────────────────────────────────────────────────┤  Hold: 0s              │
│  Altitude Profile                              │  [Delete] [Move Up]    │
│  ┌──────────────────────────────────────┐     │                        │
│  │    ╱╲                                │     ├────────────────────────┤
│  │   ╱  ╲____                          │     │  Waypoint List         │
│  │  ╱        ╲                         │     │  ────────────────────  │
│  │ ╱          ╲                        │     │  1. Takeoff (20m)      │
│  └──────────────────────────────────────┘     │  2. Waypoint (50m)     │
│                                                │  3. Waypoint (75m)  *  │
└────────────────────────────────────────────────┴────────────────────────┘
```

## Типы команд

| Тип | Описание | Параметры |
|-----|----------|-----------|
| TAKEOFF | Взлёт | altitude |
| WAYPOINT | Точка маршрута | lat, lon, alt, speed, hold_time |
| LOITER | Кружение | center, radius, turns, direction |
| ROI | Точка интереса | lat, lon, alt |
| LAND | Посадка | lat, lon (опционально) |
| RTL | Возврат домой | altitude |

## Что нужно реализовать

### 1. Store для миссии

```typescript
// stores/mission.ts
interface Waypoint {
  id: string;
  type: WaypointType;
  lat: number;
  lon: number;
  alt: number;
  params: WaypointParams;
}

interface Mission {
  name: string;
  home: { lat: number; lon: number; alt: number };
  waypoints: Waypoint[];
}

export const mission = writable<Mission>(createEmptyMission());

export function addWaypoint(lat: number, lon: number, alt: number): void;
export function removeWaypoint(id: string): void;
export function updateWaypoint(id: string, updates: Partial<Waypoint>): void;
export function moveWaypoint(fromIndex: number, toIndex: number): void;
export function calculateStats(): MissionStats;
```

### 2. Компонент карты

```svelte
<!-- MapView.svelte -->
<script>
  // Интеграция с Leaflet
  // Отображение waypoints как маркеров
  // Линии между waypoints
  // Drag-and-drop для перемещения
  // Click для добавления
</script>
```

### 3. Редактор waypoint

```svelte
<!-- WaypointEditor.svelte -->
<script>
  export let waypoint: Waypoint;
  // Форма редактирования параметров
  // Разные поля для разных типов команд
</script>
```

### 4. Профиль высоты

```svelte
<!-- AltitudeProfile.svelte -->
<script>
  // Canvas или SVG для отрисовки профиля
  // Интерактивное редактирование высот
</script>
```

### 5. Валидация

```typescript
// validation.ts
interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export function validateMission(mission: Mission): ValidationResult {
  // Проверки:
  // - Первая команда должна быть TAKEOFF
  // - Последняя команда должна быть LAND или RTL
  // - Высоты в допустимых пределах
  // - Расстояния между точками не слишком большие
  // - Скорости в допустимых пределах
}
```

### 6. Экспорт

```typescript
// export.ts

// MAVLink waypoint format
export function exportToMAVLink(mission: Mission): string;

// QGroundControl .plan format
export function exportToQGC(mission: Mission): object;

// KML для Google Earth
export function exportToKML(mission: Mission): string;
```

## Структура проекта

```
src/
├── lib/
│   ├── components/
│   │   ├── MapView.svelte
│   │   ├── WaypointEditor.svelte
│   │   ├── WaypointList.svelte
│   │   ├── AltitudeProfile.svelte
│   │   ├── MissionInfo.svelte
│   │   ├── Toolbar.svelte
│   │   └── ValidationPanel.svelte
│   ├── stores/
│   │   ├── mission.ts
│   │   ├── selection.ts
│   │   └── settings.ts
│   ├── utils/
│   │   ├── validation.ts
│   │   ├── export.ts
│   │   ├── import.ts
│   │   └── geo.ts
│   └── types.ts
├── routes/
│   └── +page.svelte
└── app.html
```

## Запуск

```bash
cd hard/02-svelte-mission-planner
npm install
npm run dev
```

## Тестирование

```bash
npm run test
npm run test:e2e  # Playwright
```

## Форматы файлов

### QGroundControl .plan

```json
{
  "fileType": "Plan",
  "version": 1,
  "mission": {
    "items": [
      {
        "type": "SimpleItem",
        "command": 22,
        "coordinate": [55.7558, 37.6173, 20]
      }
    ]
  }
}
```

### MAVLink waypoints

```
QGC WPL 110
0  1  0  16  0  0  0  0  55.7558  37.6173  150  1
1  0  3  22  0  0  0  0  0  0  20  1
...
```

## Критерии оценки

- [ ] Интерактивная карта с waypoints
- [ ] Добавление/удаление/редактирование точек
- [ ] Разные типы команд
- [ ] Профиль высоты
- [ ] Валидация миссии
- [ ] Экспорт минимум в 2 формата
- [ ] Drag-and-drop для изменения порядка
- [ ] Сохранение в localStorage

## Подсказки

1. Используйте `@svelte-store` для реактивности
2. Leaflet Draw для интерактивного рисования
3. D3.js или Chart.js для профиля высоты
4. `svelte-dnd-action` для drag-and-drop

## Дополнительно (необязательно)

- Terrain elevation API
- Расчёт времени полёта с учётом ветра
- Undo/Redo
- Collaborative editing
