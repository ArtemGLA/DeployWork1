# Задание 5: Fullstack Drone Dashboard

**Уровень:** Сложный  
**Технологии:** Rust (backend), Svelte (frontend)  
**Время выполнения:** 12-16 часов

## Описание

Комплексное веб-приложение для мониторинга и управления БПЛА. Объединяет все навыки: backend на Rust, frontend на Svelte, работу с MAVLink и WebSocket.

## Функционал

### Backend (Rust)
1. Приём MAVLink телеметрии
2. REST API для данных
3. WebSocket для real-time обновлений
4. Команды управления дроном
5. Логирование и история

### Frontend (Svelte)
1. Dashboard с телеметрией
2. Интерактивная карта
3. Управление (arm/disarm, режимы)
4. Графики параметров
5. Алерты и уведомления

## Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Svelte Frontend                          ││
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐ ││
│  │  │ Dashboard │ │    Map    │ │  Charts   │ │  Controls   │ ││
│  │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └──────┬──────┘ ││
│  │        └─────────────┴─────────────┴──────────────┘         ││
│  │                          │                                   ││
│  └──────────────────────────┼───────────────────────────────────┘│
└─────────────────────────────┼────────────────────────────────────┘
                              │ HTTP / WebSocket
┌─────────────────────────────┼────────────────────────────────────┐
│                    Rust Backend                                  │
│  ┌──────────────────────────┼─────────────────────────────────┐ │
│  │                     Axum Server                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐   │ │
│  │  │  REST API   │  │  WebSocket  │  │  Static Files     │   │ │
│  │  └──────┬──────┘  └──────┬──────┘  └───────────────────┘   │ │
│  │         └────────────────┴───────────────────┐              │ │
│  │                                              │              │ │
│  │  ┌──────────────────┐  ┌─────────────────────┴───────────┐ │ │
│  │  │  MAVLink Client  │  │      State Manager              │ │ │
│  │  └────────┬─────────┘  └─────────────────────────────────┘ │ │
│  └───────────┼──────────────────────────────────────────────────┘ │
└──────────────┼───────────────────────────────────────────────────┘
               │ UDP
       ┌───────┴───────┐
       │ MAVLink Drone │
       │  (Emulator)   │
       └───────────────┘
```

## Структура проекта

```
backend/
├── Cargo.toml
├── src/
│   ├── main.rs
│   ├── config.rs
│   ├── mavlink/
│   │   ├── mod.rs
│   │   ├── client.rs
│   │   └── commands.rs
│   ├── api/
│   │   ├── mod.rs
│   │   ├── routes.rs
│   │   ├── handlers.rs
│   │   └── websocket.rs
│   └── state/
│       ├── mod.rs
│       └── drone.rs
└── tests/

frontend/
├── package.json
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── Dashboard.svelte
│   │   │   ├── DroneMap.svelte
│   │   │   ├── TelemetryPanel.svelte
│   │   │   ├── ControlPanel.svelte
│   │   │   ├── Charts.svelte
│   │   │   └── Alerts.svelte
│   │   ├── stores/
│   │   │   ├── drone.ts
│   │   │   ├── websocket.ts
│   │   │   └── alerts.ts
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── types.ts
│   └── routes/
│       └── +page.svelte
└── static/

docker-compose.yml
```

## API Endpoints

### REST API

```
GET  /api/drones                    # Список дронов
GET  /api/drones/:id                # Данные дрона
GET  /api/drones/:id/telemetry      # Телеметрия
GET  /api/drones/:id/history        # История
POST /api/drones/:id/command        # Отправить команду
GET  /api/health                    # Health check
```

### WebSocket

```
WS /ws

# Входящие сообщения (от сервера)
{"type": "telemetry", "drone_id": 1, "data": {...}}
{"type": "status", "drone_id": 1, "data": {...}}
{"type": "alert", "drone_id": 1, "message": "...", "level": "warning"}

# Исходящие сообщения (от клиента)
{"type": "subscribe", "drone_id": 1}
{"type": "command", "drone_id": 1, "command": "arm"}
```

### Команды

```json
{"command": "arm"}
{"command": "disarm"}
{"command": "takeoff", "altitude": 20}
{"command": "land"}
{"command": "rtl"}
{"command": "goto", "lat": 55.75, "lon": 37.61, "alt": 50}
{"command": "set_mode", "mode": "AUTO"}
```

## Что нужно реализовать

### Backend

1. **MAVLink Client** — приём и парсинг телеметрии
2. **State Manager** — хранение состояния дронов
3. **REST API** — endpoints для данных
4. **WebSocket** — real-time стриминг
5. **Command Handler** — отправка команд дрону

### Frontend

1. **Dashboard** — обзор всех дронов
2. **Telemetry Panel** — детальная телеметрия
3. **Map** — карта с позицией и траекторией
4. **Control Panel** — кнопки управления
5. **Charts** — графики параметров
6. **Alerts** — уведомления об ошибках

## Запуск

```bash
# Запуск MAVLink эмулятора
cd ../../common/mavlink-emulator
python emulator.py --auto-arm &

# Запуск backend
cd backend
cargo run

# Запуск frontend (в другом терминале)
cd frontend
npm install
npm run dev
```

Открыть http://localhost:5173

## Docker

```bash
docker-compose up
```

## Тестирование

```bash
# Backend
cd backend
cargo test

# Frontend
cd frontend
npm test
npm run test:e2e
```

## Критерии оценки

### Backend
- [ ] Приём MAVLink телеметрии
- [ ] REST API работает
- [ ] WebSocket стриминг
- [ ] Отправка команд
- [ ] Обработка ошибок

### Frontend
- [ ] Dashboard отображает дроны
- [ ] Карта с позицией
- [ ] Телеметрия обновляется real-time
- [ ] Кнопки управления работают
- [ ] Графики отрисовываются
- [ ] Адаптивная вёрстка

### Интеграция
- [ ] Frontend подключается к backend
- [ ] Данные синхронизированы
- [ ] Команды выполняются

## Подсказки

1. Начните с backend API без MAVLink
2. Затем добавьте frontend с mock данными
3. Интегрируйте MAVLink в последнюю очередь
4. Используйте `tokio::sync::broadcast` для pub/sub
5. Для графиков: Chart.js или D3

## Дополнительно (необязательно)

- Авторизация (JWT)
- Несколько пользователей
- Запись/воспроизведение полётов
- Mobile responsive UI
- Dark/Light тема
