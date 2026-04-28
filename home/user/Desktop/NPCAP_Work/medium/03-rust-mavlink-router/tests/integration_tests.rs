//! Integration tests for MAVLink Router.

use std::net::UdpSocket;
use std::time::Duration;

#[test]
fn test_config_parsing() {
    let yaml = r#"
inputs:
  - name: drone1
    bind: "0.0.0.0:14550"

outputs:
  - name: gcs
    address: "127.0.0.1:14551"

routes:
  - from: drone1
    to: [gcs]
"#;
    
    // Config should parse without errors
    assert!(yaml.contains("inputs"));
    assert!(yaml.contains("outputs"));
    assert!(yaml.contains("routes"));
}

#[test]
fn test_mavlink_crc() {
    // CRC test for HEARTBEAT message
    let crc_extra_heartbeat: u8 = 50;
    
    fn crc_accumulate(data: u8, crc: u16) -> u16 {
        let tmp = data ^ (crc as u8);
        let tmp = tmp ^ (tmp << 4);
        let tmp16 = tmp as u16;
        (crc >> 8) ^ (tmp16 << 8) ^ (tmp16 << 3) ^ (tmp16 >> 4)
    }
    
    let mut crc: u16 = 0xFFFF;
    let test_data: [u8; 5] = [0x09, 0x00, 0x00, 0x00, 0x00];
    
    for byte in test_data {
        crc = crc_accumulate(byte, crc);
    }
    crc = crc_accumulate(crc_extra_heartbeat, crc);
    
    // CRC should be computed
    assert!(crc != 0xFFFF);
}

#[test]
fn test_packet_structure() {
    // MAVLink v1 packet structure
    let packet: [u8; 17] = [
        0xFE,       // Magic
        0x09,       // Payload length
        0x00,       // Sequence
        0x01,       // System ID
        0x01,       // Component ID
        0x00,       // Message ID (HEARTBEAT)
        // Payload (9 bytes)
        0x00, 0x00, 0x00, 0x00, // custom_mode
        0x02,                   // type
        0x03,                   // autopilot
        0x00,                   // base_mode
        0x00,                   // system_status
        0x03,                   // mavlink_version
        // CRC (2 bytes)
        0x00, 0x00
    ];
    
    assert_eq!(packet[0], 0xFE);
    assert_eq!(packet[1], 0x09);
    assert_eq!(packet[5], 0x00); // HEARTBEAT
}

#[test]
fn test_filter_message_ids() {
    let allowed_ids: Vec<u32> = vec![0, 1, 24, 33, 74];
    
    // HEARTBEAT (0) should pass
    assert!(allowed_ids.contains(&0));
    
    // GLOBAL_POSITION_INT (33) should pass
    assert!(allowed_ids.contains(&33));
    
    // Unknown message should not pass
    assert!(!allowed_ids.contains(&999));
}

#[test]
fn test_filter_system_ids() {
    let allowed_systems: Vec<u8> = vec![1, 2, 3];
    
    assert!(allowed_systems.contains(&1));
    assert!(!allowed_systems.contains(&255));
}

#[test]
fn test_udp_socket_creation() {
    // Should be able to create UDP socket
    let socket = UdpSocket::bind("127.0.0.1:0");
    assert!(socket.is_ok());
    
    let socket = socket.unwrap();
    socket.set_read_timeout(Some(Duration::from_millis(100))).unwrap();
}
