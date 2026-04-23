//! Библиотека для конвертации координат WGS84 <-> UTM.
//!
//! # Примеры
//!
//! ```
//! use coordinate_converter::{WGS84, UTM, Hemisphere};
//!
//! let moscow = WGS84::new(55.7558, 37.6173).unwrap();
//! let utm = moscow.to_utm();
//! println!("UTM: {} {}E {}N", utm.zone, utm.easting, utm.northing);
//! ```
mod wgs84;
mod errors;
mod utm;

pub use wgs84::WGS84;
pub use errors::CoordinateError;
pub use utm::{Hemisphere, UTM};

