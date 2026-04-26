//! MAVLink UDP receiver.

use std::sync::Arc;
use tokio::net::UdpSocket;
use crate::state::{StateManager, DroneUpdate, Position, Attitude, Velocity, Battery, GpsStatus};
use super::MAVLinkMessage;

pub struct MAVLinkReceiver {
    socket: UdpSocket,
    state: Arc<StateManager>,
}

impl MAVLinkReceiver {
    /// Создать новый приёмник.
    pub async fn new(bind_addr: &str, state: Arc<StateManager>) -> std::io::Result<Self> {
        let socket = UdpSocket::bind(bind_addr).await?;
        Ok(Self { socket, state })
    }
    
    /// Запустить приём сообщений.
    /// 
    /// TODO: Реализуйте основной цикл приёма
    pub async fn run(&self) {
        let mut buf = [0u8; 1024];
        
        loop {
            match self.socket.recv_from(&mut buf).await {
                Ok((len, _addr)) => {
                    if let Some(msg) = MAVLinkMessage::parse(&buf[..len]) {
                        self.handle_message(msg);
                    }
                }
                Err(e) => {
                    tracing::error!("UDP receive error: {}", e);
                }
            }
        }
    }
    
    /// Обработать MAVLink сообщение.
    /// 
    /// TODO: Реализуйте обработку разных типов сообщений
    fn handle_message(&self, msg: MAVLinkMessage) {
        let mut update = DroneUpdate::default();
        
        match msg.message_id {
            0 => {
                // HEARTBEAT
                // TODO: Извлечь mode и armed из payload
            }
            33 => {
                // GLOBAL_POSITION_INT
                // TODO: Извлечь позицию из payload
                if msg.payload.len() >= 28 {
                    // Пример парсинга (упрощённый)
                    // let lat = i32::from_le_bytes(...) as f64 / 1e7;
                    // let lon = i32::from_le_bytes(...) as f64 / 1e7;
                    // update.position = Some(Position { lat, lon, ... });
                }
            }
            30 => {
                // ATTITUDE
                // TODO: Извлечь attitude из payload
            }
            74 => {
                // VFR_HUD
                // TODO: Извлечь velocity из payload
            }
            1 => {
                // SYS_STATUS
                // TODO: Извлечь battery из payload
            }
            24 => {
                // GPS_RAW_INT
                // TODO: Извлечь GPS status из payload
            }
            _ => {}
        }
        
        // Обновить состояние
        self.state.update_drone(msg.system_id, update);
    }
}
