//! HTTP API module.
//!
//! TODO: Реализуйте REST API и WebSocket endpoints.

use axum::{
    Router,
    routing::get,
    extract::{Path, Query, State, WebSocketUpgrade},
    response::{IntoResponse, Json},
    http::StatusCode,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use crate::state::StateManager;

/// Создать HTTP роутер.
///
/// TODO: Реализуйте роутинг для следующих endpoints:
/// - GET /api/v1/health — health check
/// - GET /api/v1/drones — список всех дронов
/// - GET /api/v1/drones/:id — информация о дроне
/// - GET /api/v1/drones/:id/telemetry — последняя телеметрия
/// - GET /api/v1/drones/:id/telemetry/history — история телеметрии
/// - GET /ws/telemetry — WebSocket для всех дронов
/// - GET /ws/telemetry/:id — WebSocket для конкретного дрона
pub fn create_router(state: Arc<StateManager>) -> Router {
    // TODO: Создайте роутер с endpoints
    // Используйте .route() для каждого endpoint
    // Используйте .with_state(state) для передачи состояния
    
    Router::new()
        .with_state(state)
}

/// Health check endpoint.
///
/// Возвращает JSON:
/// ```json
/// {"status": "ok", "service": "telemetry-service", "version": "0.1.0"}
/// ```
async fn health_check() -> impl IntoResponse {
    // TODO: Верните JSON со статусом
    StatusCode::NOT_IMPLEMENTED
}

/// Список всех дронов.
///
/// Возвращает массив DroneState для всех известных дронов.
async fn list_drones(
    State(state): State<Arc<StateManager>>,
) -> impl IntoResponse {
    // TODO: Получите список дронов из state и верните как JSON
    StatusCode::NOT_IMPLEMENTED
}

/// Информация о конкретном дроне.
///
/// Возвращает DroneState или 404 если дрон не найден.
async fn get_drone(
    State(state): State<Arc<StateManager>>,
    Path(id): Path<u8>,
) -> impl IntoResponse {
    // TODO: Найдите дрон по id
    // Верните JSON если найден, 404 если нет
    StatusCode::NOT_IMPLEMENTED
}

/// Последняя телеметрия дрона.
///
/// Возвращает JSON с полями:
/// - drone_id, timestamp, position, attitude, velocity, battery, gps, mode, armed, online
async fn get_telemetry(
    State(state): State<Arc<StateManager>>,
    Path(id): Path<u8>,
) -> impl IntoResponse {
    // TODO: Получите телеметрию дрона и верните как JSON
    StatusCode::NOT_IMPLEMENTED
}

/// Query параметры для истории.
#[derive(Debug, Deserialize)]
struct HistoryQuery {
    /// Начало временного диапазона (unix ms)
    from: Option<u64>,
    /// Конец временного диапазона (unix ms)
    to: Option<u64>,
    /// Максимальное количество записей
    limit: Option<usize>,
}

/// История телеметрии дрона.
///
/// Поддерживает query параметры: from, to, limit
async fn get_history(
    State(state): State<Arc<StateManager>>,
    Path(id): Path<u8>,
    Query(query): Query<HistoryQuery>,
) -> impl IntoResponse {
    // TODO: Получите историю телеметрии с учётом фильтров
    // Используйте state.get_history(id, from, to, limit)
    StatusCode::NOT_IMPLEMENTED
}

/// WebSocket handler для всех дронов.
///
/// Клиент подключается и получает обновления телеметрии
/// от всех дронов в реальном времени.
async fn ws_all_handler(
    ws: WebSocketUpgrade,
    State(state): State<Arc<StateManager>>,
) -> impl IntoResponse {
    // TODO: Примите WebSocket соединение
    // ws.on_upgrade(|socket| handle_ws_connection(socket, state, None))
    StatusCode::NOT_IMPLEMENTED
}

/// WebSocket handler для конкретного дрона.
async fn ws_drone_handler(
    ws: WebSocketUpgrade,
    State(state): State<Arc<StateManager>>,
    Path(id): Path<u8>,
) -> impl IntoResponse {
    // TODO: Примите WebSocket соединение с фильтром по drone_id
    StatusCode::NOT_IMPLEMENTED
}

/// Обработка WebSocket соединения.
///
/// TODO: Реализуйте:
/// 1. Подписку на broadcast канал из StateManager
/// 2. Цикл отправки обновлений клиенту
/// 3. Фильтрацию по drone_id если указан
/// 4. Обработку отключения клиента
async fn handle_ws_connection(
    socket: axum::extract::ws::WebSocket,
    state: Arc<StateManager>,
    filter_id: Option<u8>,
) {
    // TODO: Реализуйте WebSocket логику
    //
    // Подсказки:
    // - Используйте state.subscribe() для получения Receiver
    // - Используйте tokio::select! для одновременного ожидания
    //   сообщений от broadcast и от клиента
    // - Сериализуйте TelemetryUpdate в JSON перед отправкой
    // - Фильтруйте по filter_id если Some
}
