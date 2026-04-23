/// Ошибки при работе с координатами.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum CoordinateError {
    /// Широта вне диапазона [-90, 90]
    InvalidLatitude(f64),
    /// Долгота вне диапазона [-180, 180]
    InvalidLongitude(f64),
    /// Некорректная UTM зона
    InvalidZone(u8),
}

impl std::fmt::Display for CoordinateError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InvalidLatitude(lat) => write!(f, "Invalid latitude: {}", lat),
            Self::InvalidLongitude(lon) => write!(f, "Invalid longitude: {}", lon),
            Self::InvalidZone(zone) => write!(f, "Invalid UTM zone: {}", zone),
        }
    }
}

impl std::error::Error for CoordinateError {}