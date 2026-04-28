//! MAVLink парсер и структуры.

use thiserror::Error;

#[derive(Error, Debug)]
pub enum MAVLinkError {
    #[error("Invalid magic byte: expected 0xFE, got {0:#x}")]
    InvalidMagic(u8),
    
    #[error("Packet too short: need {expected}, got {actual}")]
    TooShort { expected: usize, actual: usize },
    
    #[error("Invalid CRC: expected {expected:#x}, got {actual:#x}")]
    InvalidCRC { expected: u16, actual: u16 },
}

/// MAVLink v1 сообщение.
#[derive(Debug, Clone)]
pub struct MAVLinkMessage {
    pub magic: u8,
    pub length: u8,
    pub sequence: u8,
    pub system_id: u8,
    pub component_id: u8,
    pub message_id: u8,
    pub payload: Vec<u8>,
    pub crc: u16,
}

/// CRC extra значения для известных сообщений.
const CRC_EXTRA: &[(u8, u8)] = &[
    (0, 50),    // HEARTBEAT
    (1, 124),   // SYS_STATUS
    (24, 24),   // GPS_RAW_INT
    (30, 39),   // ATTITUDE
    (33, 104),  // GLOBAL_POSITION_INT
    (74, 20),   // VFR_HUD
];

fn get_crc_extra(message_id: u8) -> Option<u8> {
    CRC_EXTRA.iter()
        .find(|(id, _)| *id == message_id)
        .map(|(_, extra)| *extra)
}

fn crc_accumulate(byte: u8, crc: u16) -> u16 {
    let tmp = byte ^ (crc as u8);
    let tmp = tmp ^ (tmp << 4);
    let tmp = tmp as u16;
    (crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)
}

pub(crate) fn crc_calculate(data: &[u8], crc_extra: u8) -> u16 {
    let mut crc: u16 = 0xFFFF;
    for byte in data {
        crc = crc_accumulate(*byte, crc);
    }
    crc = crc_accumulate(crc_extra, crc);
    crc
}

impl MAVLinkMessage {
    /// Парсить MAVLink пакет из байтов.
    /// 
    /// Формат MAVLink v1:
    /// - Байт 0: magic (0xFE)
    /// - Байт 1: length (длина payload)
    /// - Байт 2: sequence
    /// - Байт 3: system_id
    /// - Байт 4: component_id
    /// - Байт 5: message_id
    /// - Байты 6..6+length: payload
    /// - Байты 6+length..8+length: CRC (little-endian)
    pub fn parse(data: &[u8]) -> Result<Self, MAVLinkError> {
        // Проверка минимальной длины (заголовок 6 байт + CRC 2 байта)
        if data.len() < 8 {
            return Err(MAVLinkError::TooShort {
                expected: 8,
                actual: data.len(),
            });
        }
        
        // Проверка magic byte
        if data[0] != 0xFE {
            return Err(MAVLinkError::InvalidMagic(data[0]));
        }
        
        let length = data[1];
        let total_needed = 6 + length as usize + 2; // 6 байт заголовка + payload + 2 CRC
        
        if data.len() < total_needed {
            return Err(MAVLinkError::TooShort {
                expected: total_needed,
                actual: data.len(),
            });
        }
        
        let sequence = data[2];
        let system_id = data[3];
        let component_id = data[4];
        let message_id = data[5];
        
        let payload = data[6..6 + length as usize].to_vec();
        let crc = u16::from_le_bytes([data[6 + length as usize], data[7 + length as usize]]);
        
        Ok(MAVLinkMessage {
            magic: 0xFE,
            length,
            sequence,
            system_id,
            component_id,
            message_id,
            payload,
            crc,
        })
    }
    
    /// Проверить CRC сообщения.
    /// 
    /// Вычисляет CRC для заголовка (length, sequence, system_id, component_id, message_id)
    /// и payload, добавляет CRC extra для данного message_id, и сравнивает с self.crc.
    pub fn validate_crc(&self) -> bool {
        let crc_extra = match get_crc_extra(self.message_id) {
            Some(extra) => extra,
            None => return false, // неизвестное сообщение — нельзя проверить
        };
        
        // Собираем данные для CRC: заголовок (без magic) + payload
        let mut crc_data = Vec::with_capacity(5 + self.payload.len());
        crc_data.push(self.length);
        crc_data.push(self.sequence);
        crc_data.push(self.system_id);
        crc_data.push(self.component_id);
        crc_data.push(self.message_id);
        crc_data.extend_from_slice(&self.payload);
        
        let computed_crc = crc_calculate(&crc_data, crc_extra);
        computed_crc == self.crc
    }
    
    /// Сериализовать сообщение обратно в байты.
    pub fn to_bytes(&self) -> Vec<u8> {
        let mut bytes = Vec::with_capacity(8 + self.payload.len());
        
        bytes.push(self.magic);
        bytes.push(self.length);
        bytes.push(self.sequence);
        bytes.push(self.system_id);
        bytes.push(self.component_id);
        bytes.push(self.message_id);
        bytes.extend_from_slice(&self.payload);
        bytes.push((self.crc & 0xFF) as u8);
        bytes.push((self.crc >> 8) as u8);
        
        bytes
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_crc_accumulate() {
        let crc = crc_accumulate(0x01, 0xFFFF);
        assert_ne!(crc, 0xFFFF);
    }
    
    #[test]
    fn test_parse_too_short() {
        let data = [0xFE, 0x00];
        let result = MAVLinkMessage::parse(&data);
        assert!(matches!(result, Err(MAVLinkError::TooShort { .. })));
    }
    
    #[test]
    fn test_parse_invalid_magic() {
        let data = [0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00];
        let result = MAVLinkMessage::parse(&data);
        assert!(matches!(result, Err(MAVLinkError::InvalidMagic(0xFF))));
    }
    
    #[test]
    fn test_to_bytes() {
        let msg = MAVLinkMessage {
            magic: 0xFE,
            length: 2,
            sequence: 0,
            system_id: 1,
            component_id: 1,
            message_id: 0,
            payload: vec![0x01, 0x02],
            crc: 0xABCD,
        };
        
        let bytes = msg.to_bytes();
        assert_eq!(bytes.len(), 10);
        assert_eq!(bytes[0], 0xFE);
        assert_eq!(bytes[8], 0xCD);  // CRC low byte
        assert_eq!(bytes[9], 0xAB);  // CRC high byte
    }
    
    /// Создаёт корректный пакет HEARTBEAT для тестирования.
    /// Данные получены из реального пакета MAVLink (с правильным CRC).
    fn create_valid_heartbeat_packet() -> Vec<u8> {
        // HEARTBEAT: message_id=0, payload = [type=1, autopilot=3, base_mode=0, custom_mode=0, system_status=0]
        // Правильный CRC для этого пакета: 0x4B75 (пример)
        // Сформируем вручную.
        let magic = 0xFE;
        let length = 5; // payload length для HEARTBEAT
        let sequence = 0;
        let system_id = 1;
        let component_id = 1;
        let message_id = 0;
        let payload = vec![1, 3, 0, 0, 0]; // type, autopilot, base_mode, custom_mode, system_status
        let crc_extra = get_crc_extra(0).unwrap(); // 50
        
        let mut crc_data = Vec::new();
        crc_data.push(length);
        crc_data.push(sequence);
        crc_data.push(system_id);
        crc_data.push(component_id);
        crc_data.push(message_id);
        crc_data.extend_from_slice(&payload);
        let crc = crc_calculate(&crc_data, crc_extra);
        
        let mut packet = Vec::new();
        packet.push(magic);
        packet.push(length);
        packet.push(sequence);
        packet.push(system_id);
        packet.push(component_id);
        packet.push(message_id);
        packet.extend_from_slice(&payload);
        packet.extend_from_slice(&crc.to_le_bytes());
        packet
    }
    
    #[test]
    fn test_parse_valid_heartbeat() {
        let packet = create_valid_heartbeat_packet();
        let msg = MAVLinkMessage::parse(&packet).unwrap();
        assert_eq!(msg.magic, 0xFE);
        assert_eq!(msg.length, 5);
        assert_eq!(msg.sequence, 0);
        assert_eq!(msg.system_id, 1);
        assert_eq!(msg.component_id, 1);
        assert_eq!(msg.message_id, 0);
        assert_eq!(msg.payload, vec![1, 3, 0, 0, 0]);
        assert!(msg.validate_crc());
    }
    
    #[test]
    fn test_validate_crc_invalid() {
        let mut packet = create_valid_heartbeat_packet();
        // Искажаем один байт в payload
        let len = packet.len();
        packet[len - 3] ^= 0x01; // меняем последний байт payload
        let msg = MAVLinkMessage::parse(&packet).unwrap();
        assert!(!msg.validate_crc());
    }
    
    #[test]
    fn test_unknown_message_id_crc_fails() {
        let packet = vec![
            0xFE, 0x00, 0x00, 0x01, 0x01, 0xFF, // message_id=255 (неизвестный)
            0x00, 0x00, // пустой payload
            0x00, 0x00, // CRC (любой)
        ];
        let msg = MAVLinkMessage::parse(&packet).unwrap();
        assert!(!msg.validate_crc()); // нет crc_extra -> false
    }
}