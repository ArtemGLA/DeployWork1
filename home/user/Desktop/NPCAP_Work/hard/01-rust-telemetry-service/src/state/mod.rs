//! State management module.
//!
//! TODO: Реализуйте управление состоянием дронов и историей телеметрии.

use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};
use std::sync::RwLock;
use std::time::{Duration, Instant};
use tokio::sync::broadcast;

const MAX_HISTORY_SIZE: usize = 10000;
const DRONE_TIMEOUT_SECS: u64 = 30;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Position {
    pub lat: f64,
    pub lon: f64,
    pub alt: f64,
    pub relative_alt: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Attitude {
    pub roll: f64,
    pub pitch: f64,
    pub yaw: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Velocity {
    pub vx: f64,
    pub vy: f64,
    pub vz: f64,
    pub groundspeed: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Battery {
    pub voltage: f64,
    pub current: f64,
    pub remaining: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpsStatus {
    pub fix_type: u8,
    pub satellites: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DroneState {
    pub id: u8,
    pub last_seen_ms: u64,
    pub position: Position,
    pub attitude: Attitude,
    pub velocity: Velocity,
    pub battery: Battery,
    pub gps: GpsStatus,
    pub mode: String,
    pub armed: bool,
    pub online: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TelemetryRecord {
    pub timestamp: u64,
    pub position: Position,
    pub attitude: Attitude,
    pub velocity: Velocity,
    pub battery: Battery,
}

#[derive(Debug, Clone)]
pub struct TelemetryUpdate {
    pub drone_id: u8,
    pub timestamp: u64,
    pub state: DroneState,
}

/// Частичное обновление состояния дрона.
#[derive(Debug, Clone, Default)]
pub struct DroneUpdate {
    pub position: Option<Position>,
    pub attitude: Option<Attitude>,
    pub velocity: Option<Velocity>,
    pub battery: Option<Battery>,
    pub gps: Option<GpsStatus>,
    pub mode: Option<String>,
    pub armed: Option<bool>,
}

struct DroneStateInternal {
    state: DroneState,
    last_update: Instant,
}

/// State Manager - управление состоянием дронов.
///
/// TODO: Реализуйте все методы этой структуры.
pub struct StateManager {
    drones: RwLock<HashMap<u8, DroneStateInternal>>,
    history: RwLock<HashMap<u8, VecDeque<TelemetryRecord>>>,
    tx: broadcast::Sender<TelemetryUpdate>,
}

impl StateManager {
    pub fn new() -> Self {
        let (tx, _) = broadcast::channel(1000);
        Self {
            drones: RwLock::new(HashMap::new()),
            history: RwLock::new(HashMap::new()),
            tx,
        }
    }
    
    /// Подписаться на обновления телеметрии.
    pub fn subscribe(&self) -> broadcast::Receiver<TelemetryUpdate> {
        self.tx.subscribe()
    }
    
    /// Получить список всех дронов.
    ///
    /// TODO: Реализуйте получение списка дронов
    ///
    /// Требования:
    /// 1. Получить read lock на self.drones
    /// 2. Для каждого дрона проверить timeout (online = last_update < DRONE_TIMEOUT_SECS)
    /// 3. Вернуть список DroneState
    pub fn get_all_drones(&self) -> Vec<DroneState> {
        // Ваш код здесь
        Vec::new()
    }
    
    /// Получить состояние конкретного дрона.
    ///
    /// TODO: Реализуйте поиск дрона по id
    ///
    /// Требования:
    /// 1. Получить read lock
    /// 2. Найти дрон по id
    /// 3. Обновить поле online на основе timeout
    /// 4. Вернуть Some(DroneState) или None
    pub fn get_drone(&self, id: u8) -> Option<DroneState> {
        // Ваш код здесь
        None
    }
    
    /// Обновить состояние дрона.
    ///
    /// TODO: Реализуйте обновление состояния
    ///
    /// Требования:
    /// 1. Получить write lock
    /// 2. Если дрон не существует — создать с дефолтными значениями
    /// 3. Применить все непустые поля из DroneUpdate
    /// 4. Обновить last_update и last_seen_ms
    /// 5. Добавить запись в историю
    /// 6. Отправить TelemetryUpdate через self.tx.send()
    pub fn update_drone(&self, id: u8, update: DroneUpdate) {
        // Ваш код здесь
    }
    
    /// Добавить запись в историю.
    ///
    /// TODO: Реализуйте добавление в историю
    ///
    /// Требования:
    /// 1. Получить write lock на history
    /// 2. Если история превышает MAX_HISTORY_SIZE — удалить старые записи
    /// 3. Добавить новую запись TelemetryRecord
    fn add_to_history(&self, id: u8, record: TelemetryRecord) {
        // Ваш код здесь
    }
    
    /// Получить историю телеметрии.
    ///
    /// TODO: Реализуйте фильтрацию истории
    ///
    /// Требования:
    /// 1. Получить read lock на history
    /// 2. Отфильтровать записи по временному диапазону [from, to]
    /// 3. Ограничить количество записей параметром limit
    /// 4. Вернуть Vec<TelemetryRecord>
    pub fn get_history(&self, id: u8, from: u64, to: u64, limit: usize) -> Vec<TelemetryRecord> {
        // Ваш код здесь
        Vec::new()
    }
}
