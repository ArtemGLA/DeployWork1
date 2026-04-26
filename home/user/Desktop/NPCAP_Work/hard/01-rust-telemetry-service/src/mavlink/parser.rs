//! MAVLink parser.

#[derive(Debug, Clone)]
pub struct MAVLinkMessage {
    pub system_id: u8,
    pub component_id: u8,
    pub message_id: u8,
    pub payload: Vec<u8>,
}

impl MAVLinkMessage {
    /// Парсить MAVLink пакет.
    /// 
    /// TODO: Реализуйте парсинг (аналогично предыдущим заданиям)
    pub fn parse(data: &[u8]) -> Option<Self> {
        if data.len() < 8 {
            return None;
        }
        
        if data[0] != 0xFE {
            return None;
        }
        
        let len = data[1] as usize;
        if data.len() < 8 + len {
            return None;
        }
        
        Some(Self {
            system_id: data[3],
            component_id: data[4],
            message_id: data[5],
            payload: data[6..6 + len].to_vec(),
        })
    }
}
