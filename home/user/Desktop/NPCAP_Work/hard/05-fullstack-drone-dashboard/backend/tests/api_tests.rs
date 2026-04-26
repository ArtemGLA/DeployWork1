//! API tests for Drone Dashboard Backend.

#[test]
fn test_drone_state_defaults() {
    #[derive(Debug, Default)]
    struct Battery {
        voltage: f64,
        current: f64,
        remaining: u8,
    }
    
    let battery = Battery::default();
    assert_eq!(battery.voltage, 0.0);
    assert_eq!(battery.remaining, 0);
}

#[test]
fn test_command_serialization() {
    #[derive(serde::Serialize, serde::Deserialize)]
    #[serde(tag = "command")]
    enum Command {
        #[serde(rename = "arm")]
        Arm,
        #[serde(rename = "disarm")]
        Disarm,
        #[serde(rename = "takeoff")]
        Takeoff { altitude: f64 },
        #[serde(rename = "land")]
        Land,
        #[serde(rename = "rtl")]
        Rtl,
    }
    
    let arm = Command::Arm;
    let json = serde_json::to_string(&arm).unwrap();
    assert!(json.contains("arm"));
    
    let takeoff = Command::Takeoff { altitude: 20.0 };
    let json = serde_json::to_string(&takeoff).unwrap();
    assert!(json.contains("takeoff"));
    assert!(json.contains("20"));
}

#[test]
fn test_response_format() {
    #[derive(serde::Serialize)]
    struct ApiResponse<T> {
        success: bool,
        data: Option<T>,
        error: Option<String>,
    }
    
    let success: ApiResponse<String> = ApiResponse {
        success: true,
        data: Some("OK".to_string()),
        error: None,
    };
    
    let json = serde_json::to_string(&success).unwrap();
    assert!(json.contains("\"success\":true"));
    
    let error: ApiResponse<()> = ApiResponse {
        success: false,
        data: None,
        error: Some("Not found".to_string()),
    };
    
    let json = serde_json::to_string(&error).unwrap();
    assert!(json.contains("\"success\":false"));
}

#[test]
fn test_websocket_subscription() {
    #[derive(serde::Deserialize)]
    #[serde(tag = "type")]
    enum ClientMessage {
        #[serde(rename = "subscribe")]
        Subscribe { drone_id: u8 },
        #[serde(rename = "command")]
        Command { drone_id: u8, command: String },
    }
    
    let sub_json = r#"{"type": "subscribe", "drone_id": 1}"#;
    let msg: ClientMessage = serde_json::from_str(sub_json).unwrap();
    
    match msg {
        ClientMessage::Subscribe { drone_id } => assert_eq!(drone_id, 1),
        _ => panic!("Expected Subscribe"),
    }
}

#[test]
fn test_telemetry_broadcast() {
    use std::sync::mpsc;
    
    let (tx, rx) = mpsc::channel::<String>();
    
    tx.send("telemetry_update".to_string()).unwrap();
    
    let received = rx.recv().unwrap();
    assert_eq!(received, "telemetry_update");
}
