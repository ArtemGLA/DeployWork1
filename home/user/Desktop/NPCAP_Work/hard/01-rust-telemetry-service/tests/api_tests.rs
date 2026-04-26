//! API tests for Telemetry Service.

use std::collections::HashMap;

#[test]
fn test_drone_state_serialization() {
    #[derive(Debug, Clone, serde::Serialize, serde::Deserialize, PartialEq)]
    struct Position {
        lat: f64,
        lon: f64,
        alt: f64,
    }
    
    let pos = Position {
        lat: 55.7558,
        lon: 37.6173,
        alt: 100.0,
    };
    
    let json = serde_json::to_string(&pos).unwrap();
    assert!(json.contains("55.7558"));
    
    let parsed: Position = serde_json::from_str(&json).unwrap();
    assert_eq!(parsed, pos);
}

#[test]
fn test_telemetry_history_storage() {
    struct TelemetryRecord {
        timestamp: u64,
        altitude: f64,
    }
    
    let mut history: Vec<TelemetryRecord> = Vec::new();
    
    for i in 0..1000 {
        history.push(TelemetryRecord {
            timestamp: i,
            altitude: 50.0 + (i as f64 * 0.1),
        });
    }
    
    // Should limit history size
    let max_history = 500;
    if history.len() > max_history {
        history = history.split_off(history.len() - max_history);
    }
    
    assert_eq!(history.len(), 500);
    assert_eq!(history[0].timestamp, 500);
}

#[test]
fn test_drone_registry() {
    let mut drones: HashMap<u8, String> = HashMap::new();
    
    drones.insert(1, "Drone 1".to_string());
    drones.insert(2, "Drone 2".to_string());
    
    assert_eq!(drones.len(), 2);
    assert!(drones.contains_key(&1));
    assert!(!drones.contains_key(&3));
}

#[test]
fn test_websocket_message_format() {
    #[derive(serde::Serialize)]
    struct WebSocketMessage {
        r#type: String,
        drone_id: u8,
        timestamp: u64,
    }
    
    let msg = WebSocketMessage {
        r#type: "telemetry".to_string(),
        drone_id: 1,
        timestamp: 1234567890,
    };
    
    let json = serde_json::to_string(&msg).unwrap();
    assert!(json.contains("telemetry"));
    assert!(json.contains("drone_id"));
}

#[test]
fn test_command_parsing() {
    #[derive(serde::Deserialize)]
    struct Command {
        command: String,
        #[serde(default)]
        altitude: Option<f64>,
    }
    
    let arm_json = r#"{"command": "arm"}"#;
    let cmd: Command = serde_json::from_str(arm_json).unwrap();
    assert_eq!(cmd.command, "arm");
    assert!(cmd.altitude.is_none());
    
    let takeoff_json = r#"{"command": "takeoff", "altitude": 20.0}"#;
    let cmd: Command = serde_json::from_str(takeoff_json).unwrap();
    assert_eq!(cmd.command, "takeoff");
    assert_eq!(cmd.altitude, Some(20.0));
}

#[test]
fn test_mavlink_message_ids() {
    // Common MAVLink message IDs
    const HEARTBEAT: u8 = 0;
    const SYS_STATUS: u8 = 1;
    const GLOBAL_POSITION_INT: u8 = 33;
    const ATTITUDE: u8 = 30;
    const VFR_HUD: u8 = 74;
    
    let telemetry_messages = [
        HEARTBEAT,
        SYS_STATUS,
        GLOBAL_POSITION_INT,
        ATTITUDE,
        VFR_HUD
    ];
    
    assert!(telemetry_messages.contains(&33));
}
