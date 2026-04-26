//! Configuration.

use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct Config {
    pub mavlink_port: u16,
    pub http_port: u16,
    pub history_size: usize,
    pub drone_timeout_secs: u64,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            mavlink_port: 14550,
            http_port: 8080,
            history_size: 10000,
            drone_timeout_secs: 30,
        }
    }
}
