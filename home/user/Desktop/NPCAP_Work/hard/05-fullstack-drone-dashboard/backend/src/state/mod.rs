//! Application state management.
//!
//! TODO: Реализуйте управление состоянием дронов.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::RwLock;
use tokio::sync::broadcast;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DroneState {
    pub id: u8,
    pub name: String,
    pub connected: bool,
    pub armed: bool,
    pub mode: String,
    pub position: Position,
    pub attitude: Attitude,
    pub velocity: Velocity,
    pub battery: Battery,
    pub gps: GpsStatus,
    pub last_update: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Position {
    pub lat: f64,
    pub lon: f64,
    pub alt: f64,
    pub relative_alt: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Attitude {
    pub roll: f64,
    pub pitch: f64,
    pub yaw: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Velocity {
    pub vx: f64,
    pub vy: f64,
    pub vz: f64,
    pub groundspeed: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Battery {
    pub voltage: f64,
    pub current: f64,
    pub remaining: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct GpsStatus {
    pub fix_type: u8,
    pub satellites: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TelemetryUpdate {
    pub drone_id: u8,
    pub timestamp: u64,
    pub data: DroneState,
}

impl Default for DroneState {
    fn default() -> Self {
        Self {
            id: 1,
            name: "Drone 1".to_string(),
            connected: false,
            armed: false,
            mode: "STABILIZE".to_string(),
            position: Position::default(),
            attitude: Attitude::default(),
            velocity: Velocity::default(),
            battery: Battery { voltage: 12.6, current: 0.0, remaining: 100 },
            gps: GpsStatus::default(),
            last_update: 0,
        }
    }
}

/// Application state.
///
/// TODO: Реализуйте все методы.
pub struct AppState {
    pub drones: RwLock<HashMap<u8, DroneState>>,
    pub telemetry_tx: broadcast::Sender<TelemetryUpdate>,
}

impl AppState {
    pub fn new() -> Self {
        let (tx, _) = broadcast::channel(100);
        
        Self {
            drones: RwLock::new(HashMap::new()),
            telemetry_tx: tx,
        }
    }
    
    /// Получить состояние дрона по ID.
    ///
    /// TODO: Реализуйте поиск дрона
    pub fn get_drone(&self, id: u8) -> Option<DroneState> {
        // Ваш код здесь
        None
    }
    
    /// Получить список всех дронов.
    ///
    /// TODO: Реализуйте получение списка
    pub fn get_all_drones(&self) -> Vec<DroneState> {
        // Ваш код здесь
        Vec::new()
    }
    
    /// Обновить состояние дрона.
    ///
    /// TODO: Реализуйте обновление
    ///
    /// Требования:
    /// 1. Записать состояние в HashMap
    /// 2. Отправить TelemetryUpdate через telemetry_tx
    pub fn update_drone(&self, state: DroneState) {
        // Ваш код здесь
    }
    
    /// Подписаться на обновления телеметрии.
    pub fn subscribe(&self) -> broadcast::Receiver<TelemetryUpdate> {
        self.telemetry_tx.subscribe()
    }
}
