# Задание 1: Telemetry Service

**Уровень:** Сложный  
**Технологии:** Rust, axum, tokio, WebSocket  
**Время выполнения:** 8-12 часов

## Описание

Telemetry Service — это микросервис, который:
- Принимает MAVLink телеметрию от дронов
- Хранит историю данных
- Предоставляет REST API для запросов
- Стримит данные клиентам через WebSocket

## Архитектура

```
                          ┌──────────────────────────┐
MAVLink UDP ──────────────▶│                          │
(from drones)             │    Telemetry Service     │
                          │                          │
                          │  ┌────────────────────┐  │
                          │  │   MAVLink Parser   │  │
                          │  └─────────┬──────────┘  │
                          │            │             │
                          │  ┌─────────▼──────────┐  │
                          │  │   State Manager    │  │
                          │  │   (in-memory DB)   │  │
                          │  └─────────┬──────────┘  │
                          │            │             │
                          │  ┌─────────▼──────────┐  │
REST API  ◀───────────────│  │    HTTP Server     │──▶ WebSocket
(history, status)         │  │     (axum)         │   (live stream)
                          │  └────────────────────┘  │
                          └──────────────────────────┘
```

## API

### REST Endpoints

```
GET  /api/v1/drones              # Список всех дронов
GET  /api/v1/drones/{id}         # Информация о дроне
GET  /api/v1/drones/{id}/telemetry        # Последняя телеметрия
GET  /api/v1/drones/{id}/telemetry/history # История телеметрии
     ?from=timestamp&to=timestamp&limit=100
GET  /api/v1/drones/{id}/position/history  # История позиций (для траектории)
GET  /api/v1/health              # Health check
```

### WebSocket

```
WS   /ws/telemetry               # Стрим телеметрии всех дронов
WS   /ws/telemetry/{id}          # Стрим телеметрии конкретного дрона
```

Формат сообщений WebSocket:
```json
{
  "type": "telemetry",
  "drone_id": 1,
  "timestamp": 1709640000,
  "data": {
    "position": {"lat": 55.7558, "lon": 37.6173, "alt": 150},
    "attitude": {"roll": 0.02, "pitch": 0.01, "yaw": 1.57},
    "velocity": {"vx": 5.2, "vy": 3.1, "vz": -0.5},
    "battery": {"voltage": 12.5, "remaining": 85},
    "gps": {"fix_type": 3, "satellites": 12}
  }
}
```

## Что нужно реализовать

### 1. MAVLink приёмник

```rust
pub struct MAVLinkReceiver {
    socket: UdpSocket,
    sender: broadcast::Sender<MAVLinkMessage>,
}

impl MAVLinkReceiver {
    pub async fn new(bind_addr: &str) -> Result<Self>;
    pub async fn run(&self);
}
```

### 2. State Manager

```rust
pub struct DroneState {
    pub id: u8,
    pub last_seen: Instant,
    pub position: Position,
    pub attitude: Attitude,
    pub velocity: Velocity,
    pub battery: Battery,
    pub gps: GpsStatus,
    pub mode: FlightMode,
    pub armed: bool,
}

pub struct StateManager {
    drones: RwLock<HashMap<u8, DroneState>>,
    history: RwLock<HashMap<u8, VecDeque<TelemetryRecord>>>,
}

impl StateManager {
    pub fn update(&self, msg: &MAVLinkMessage);
    pub fn get_drone(&self, id: u8) -> Option<DroneState>;
    pub fn get_all_drones(&self) -> Vec<DroneState>;
    pub fn get_history(&self, id: u8, from: u64, to: u64, limit: usize) -> Vec<TelemetryRecord>;
}
```

### 3. HTTP сервер

```rust
pub fn create_router(state: Arc<StateManager>) -> Router {
    Router::new()
        .route("/api/v1/drones", get(list_drones))
        .route("/api/v1/drones/:id", get(get_drone))
        .route("/api/v1/drones/:id/telemetry", get(get_telemetry))
        .route("/api/v1/drones/:id/telemetry/history", get(get_history))
        .route("/ws/telemetry", get(ws_handler))
        .route("/ws/telemetry/:id", get(ws_drone_handler))
        .route("/api/v1/health", get(health_check))
        .with_state(state)
}
```

### 4. WebSocket handler

```rust
async fn ws_handler(
    ws: WebSocketUpgrade,
    State(state): State<Arc<StateManager>>,
) -> impl IntoResponse {
    ws.on_upgrade(|socket| handle_socket(socket, state))
}

async fn handle_socket(mut socket: WebSocket, state: Arc<StateManager>) {
    // Подписаться на обновления телеметрии
    // Отправлять клиенту JSON при каждом обновлении
}
```

## Структура проекта

```
src/
├── main.rs
├── config.rs          # Конфигурация
├── mavlink/
│   ├── mod.rs
│   ├── parser.rs      # Парсер MAVLink
│   └── receiver.rs    # UDP приёмник
├── state/
│   ├── mod.rs
│   ├── manager.rs     # State manager
│   ├── drone.rs       # Структуры данных дрона
│   └── history.rs     # Хранение истории
├── api/
│   ├── mod.rs
│   ├── routes.rs      # REST endpoints
│   ├── handlers.rs    # Request handlers
│   └── websocket.rs   # WebSocket
└── error.rs           # Error types

tests/
├── integration_test.rs
└── api_test.rs
```

## Запуск

```bash
cd hard/01-rust-telemetry-service

# Сборка
cargo build --release

# Запуск
cargo run -- --mavlink-port 14550 --http-port 8080

# С конфигурацией
cargo run -- --config config.toml
```

## Тестирование

```bash
# Unit тесты
cargo test

# Integration тесты (требуют эмулятор)
cargo test --test integration_test

# Ручное тестирование
# Терминал 1: запуск сервиса
cargo run

# Терминал 2: запуск эмулятора
python ../../common/mavlink-emulator/emulator.py

# Терминал 3: запросы к API
curl http://localhost:8080/api/v1/drones
curl http://localhost:8080/api/v1/drones/1/telemetry

# WebSocket тест
websocat ws://localhost:8080/ws/telemetry
```

## Критерии оценки

- [ ] Приём и парсинг MAVLink сообщений
- [ ] Хранение состояния дронов
- [ ] REST API работает корректно
- [ ] WebSocket стриминг работает
- [ ] История телеметрии сохраняется
- [ ] Graceful shutdown
- [ ] Обработка ошибок
- [ ] Код проходит тесты

## Подсказки

1. Используйте `tokio::sync::broadcast` для pub/sub
2. `Arc<RwLock<T>>` для shared state
3. `axum::extract::ws` для WebSocket
4. Ограничьте размер истории (circular buffer)
5. Добавьте timeout для "мёртвых" дронов

## Дополнительно (необязательно)

- Prometheus метрики
- OpenAPI/Swagger документация
- gRPC endpoint
- Persistence (SQLite/PostgreSQL)
