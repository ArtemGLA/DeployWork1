//! HTTP API module.
//!
//! TODO: Реализуйте REST API и WebSocket endpoints.

use axum::{
    Router,
    routing::{get, post},
    extract::{Path, State, WebSocketUpgrade},
    response::{IntoResponse, Json},
    http::StatusCode,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use crate::state::AppState;

/// Создать HTTP роутер.
///
/// TODO: Реализуйте все endpoints:
/// - GET /api/health — health check
/// - GET /api/drones — список дронов
/// - GET /api/drones/:id — информация о дроне
/// - GET /api/drones/:id/telemetry — телеметрия дрона
/// - POST /api/drones/:id/command — отправка команды
/// - GET /ws — WebSocket для real-time обновлений
pub fn create_router(state: Arc<AppState>) -> Router {
    // TODO: Создайте роутер с endpoints
    Router::new()
        .with_state(state)
}

/// Health check.
async fn health() -> impl IntoResponse {
    // TODO: Верните JSON {"status": "ok", "service": "drone-dashboard"}
    StatusCode::NOT_IMPLEMENTED
}

/// Список всех дронов.
async fn list_drones(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    // TODO: Получите список дронов из state
    StatusCode::NOT_IMPLEMENTED
}

/// Информация о дроне.
async fn get_drone(
    State(state): State<Arc<AppState>>,
    Path(id): Path<u8>,
) -> impl IntoResponse {
    // TODO: Найдите дрон по id, верните 404 если не найден
    StatusCode::NOT_IMPLEMENTED
}

/// Телеметрия дрона.
async fn get_telemetry(
    State(state): State<Arc<AppState>>,
    Path(id): Path<u8>,
) -> impl IntoResponse {
    // TODO: Получите и верните телеметрию
    StatusCode::NOT_IMPLEMENTED
}

#[derive(Debug, Deserialize)]
struct CommandRequest {
    command: String,
    #[serde(flatten)]
    params: serde_json::Value,
}

#[derive(Debug, Serialize)]
struct CommandResponse {
    success: bool,
    message: String,
}

/// Отправка команды дрону.
///
/// Поддерживаемые команды:
/// - arm, disarm
/// - takeoff (с параметром altitude)
/// - land, rtl
/// - goto (с параметрами lat, lon, alt)
/// - set_mode (с параметром mode)
async fn send_command(
    State(state): State<Arc<AppState>>,
    Path(id): Path<u8>,
    Json(cmd): Json<CommandRequest>,
) -> impl IntoResponse {
    // TODO: Реализуйте обработку команд
    // 1. Проверьте что дрон существует
    // 2. Валидируйте команду и параметры
    // 3. Отправьте команду (через MAVLink или mock)
    // 4. Верните результат
    StatusCode::NOT_IMPLEMENTED
}

/// WebSocket handler.
async fn ws_handler(
    ws: WebSocketUpgrade,
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    // TODO: Примите WebSocket соединение
    // ws.on_upgrade(move |socket| handle_ws(socket, state))
    StatusCode::NOT_IMPLEMENTED
}

/// Обработка WebSocket соединения.
///
/// TODO: Реализуйте WebSocket логику:
/// 1. Подпишитесь на обновления через state.subscribe()
/// 2. В цикле отправляйте обновления клиенту
/// 3. Обрабатывайте входящие сообщения (команды)
/// 4. Корректно завершайте при отключении
async fn handle_ws(
    socket: axum::extract::ws::WebSocket,
    state: Arc<AppState>,
) {
    // Ваш код здесь
    //
    // Подсказки:
    // - Используйте tokio::select! для одновременного ожидания
    // - Формат исходящих сообщений: {"type": "telemetry", "drone_id": N, "data": {...}}
    // - Формат входящих команд: {"type": "command", "drone_id": N, "command": "..."}
}
