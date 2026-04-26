//! Error types.

use thiserror::Error;

#[derive(Error, Debug)]
pub enum ServiceError {
    #[error("MAVLink error: {0}")]
    MAVLink(String),
    
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Parse error: {0}")]
    Parse(String),
    
    #[error("Drone not found: {0}")]
    DroneNotFound(u8),
}
