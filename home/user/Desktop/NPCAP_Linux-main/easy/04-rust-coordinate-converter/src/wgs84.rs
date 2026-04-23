use crate::utm::{Hemisphere, UTM};  // ← импорт из другого модуля
use crate::errors::CoordinateError;

const WGS84_A: f64 = 6378137.0; // большая полуось (м)
const WGS84_E: f64 = 0.0818191908426; // эксцентриситет
const WGS84_E2: f64 = WGS84_E * WGS84_E; // квадрат эксцентриситета
const UTM_K0: f64 = 0.9996; // масштабный коэффициент UTM
const EARTH_RADIUS: f64 = 6371000.0; // средний радиус Земли (м)

/// Координаты в системе WGS84 (широта/долгота).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct WGS84 {
    /// Широта в градусах (-90..90)
    pub lat: f64,
    /// Долгота в градусах (-180..180)
    pub lon: f64,
}

impl WGS84 {
    /// Создать координату WGS84 из градусов.
    ///
    /// # Ошибки
    ///
    /// Возвращает ошибку если координаты вне допустимого диапазона.
    ///
    /// # Примеры
    ///
    /// ```
    /// use coordinate_converter::WGS84;
    ///
    /// let point = WGS84::new(55.7558, 37.6173).unwrap();
    /// assert_eq!(point.lat, 55.7558);
    /// ```
    pub fn new(lat: f64, lon: f64) -> Result<Self, CoordinateError> {
        if !(-90.0..=90.0).contains(&lat) {
            return Err(CoordinateError::InvalidLatitude(lat));
        }
        if !(-180.0..=180.0).contains(&lon) {
            return Err(CoordinateError::InvalidLongitude(lon));
        }
        Ok(Self { lat, lon })
    }

    /// Конвертировать в координаты UTM.
    ///
    /// # Примеры
    ///
    /// ```
    /// use coordinate_converter::{WGS84, Hemisphere};
    ///
    /// let moscow = WGS84::new(55.7558, 37.6173).unwrap();
    /// let utm = moscow.to_utm();
    /// assert_eq!(utm.zone, 37);
    /// ```
    pub fn to_utm(&self) -> UTM {
        // Вычисление зоны
        let zone = ((self.lon + 180.0) / 6.0).floor() as u8 + 1;

        // Определение полушария
        let hemisphere = if self.lat >= 0.0 {
            Hemisphere::North
        } else {
            Hemisphere::South
        };

        // Центральный меридиан зоны в радианах
        let lon0 = ((zone as f64 - 1.0) * 6.0 - 180.0 + 3.0).to_radians();

        // Конвертация в радианы
        let lat = self.lat.to_radians();
        let lon = self.lon.to_radians();

        // Разница долгот от центрального меридиана
        let dlon = lon - lon0;

        // Вспомогательные вычисления для проекции Transverse Mercator
        let sin_lat = lat.sin();
        let cos_lat = lat.cos();
        let tan_lat = sin_lat / cos_lat;

        // Меридианная дуга
        let n = WGS84_A / (1.0 - WGS84_E2 * sin_lat * sin_lat).sqrt();
        let t = tan_lat * tan_lat;
        let c = WGS84_E2 * cos_lat * cos_lat / (1.0 - WGS84_E2);
        let a = dlon * cos_lat;

        // Вычисление easting и northing
        let m = self.meridian_arc_length(lat);

        let northing = UTM_K0 * (m + n * tan_lat * (a * a / 2.0 +
            (5.0 - t + 9.0 * c + 4.0 * c * c) * a * a * a * a / 24.0 +
            (61.0 - 58.0 * t + t * t + 270.0 * c - 330.0 * t * c) * a * a * a * a * a * a / 720.0));

        let easting = UTM_K0 * n * (a +
            (1.0 - t + c) * a * a * a / 6.0 +
            (5.0 - 18.0 * t + t * t + 72.0 * c - 58.0 * WGS84_E2) * a * a * a * a * a / 120.0);

        // Корректировка для южного полушария
        let northing = if matches!(hemisphere, Hemisphere::South) {
            northing + 10000000.0
        } else {
            northing
        };

        UTM {
            easting: easting + 500000.0,
            northing,
            zone,
            hemisphere,
        }
    }

    /// Вычислить длину меридианной дуги от экватора до широты
    fn meridian_arc_length(&self, lat_rad: f64) -> f64 {
    let e2 = WGS84_E2;
    let e4 = e2 * e2;
    let e6 = e4 * e2;
    
    // Коэффициенты (проверено по стандарту)
    let a0 = 1.0 - e2/4.0 - 3.0*e4/64.0 - 5.0*e6/256.0;
    let a2 = 3.0*e2/8.0 + 3.0*e4/32.0 + 45.0*e6/1024.0;
    let a4 = 15.0*e4/256.0 + 45.0*e6/1024.0;
    let a6 = 35.0*e6/3072.0;
    
    // Формула: M = a * (A0 * φ - A2 * sin(2φ) + A4 * sin(4φ) - A6 * sin(6φ))
    WGS84_A * (a0 * lat_rad 
        - a2 * (2.0 * lat_rad).sin()
        + a4 * (4.0 * lat_rad).sin()
        - a6 * (6.0 * lat_rad).sin())
}
    /// Вычислить расстояние до другой точки в метрах.
    ///
    /// Использует формулу Хаверсина для расчёта расстояния
    /// по поверхности сферы.
    ///
    /// # Примеры
    ///
    /// ```
    /// use coordinate_converter::WGS84;
    ///
    /// let moscow = WGS84::new(55.7558, 37.6173).unwrap();
    /// let spb = WGS84::new(59.9343, 30.3351).unwrap();
    /// let distance = moscow.distance_to(&spb);
    /// // ~635 км
    /// assert!(distance > 600_000.0 && distance < 700_000.0);
    /// ```
    pub fn distance_to(&self, other: &WGS84) -> f64 {
        let lat1 = self.lat.to_radians();
        let lon1 = self.lon.to_radians();
        let lat2 = other.lat.to_radians();
        let lon2 = other.lon.to_radians();

        let dlat = (lat2 - lat1) / 2.0;
        let dlon = (lon2 - lon1) / 2.0;

        let a = (dlat.sin() * dlat.sin()) + lat1.cos() * lat2.cos() * (dlon.sin() * dlon.sin());
        let c = 2.0 * a.sqrt().atan2((1.0 - a).sqrt());

        EARTH_RADIUS * c
    }

    pub fn bearing_to(&self, other: &WGS84) -> f64 {
        let lat1 = self.lat.to_radians();
        let lon1 = self.lon.to_radians();
        let lat2 = other.lat.to_radians();
        let lon2 = other.lon.to_radians();

        let dlon = lon2 - lon1;

        let y = dlon.sin() * lat2.cos();
        let x = lat1.cos() * lat2.sin() - lat1.sin() * lat2.cos() * dlon.cos();

        let bearing = y.atan2(x).to_degrees();

        // Конвертируем в диапазон 0-360
        (bearing + 360.0) % 360.0
    }

}
