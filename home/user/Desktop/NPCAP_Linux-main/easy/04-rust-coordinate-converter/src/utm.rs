use crate::wgs84::{WGS84};  // ← импорт из другого модуля

const WGS84_A: f64 = 6378137.0; // большая полуось (м)
const WGS84_E: f64 = 0.0818191908426; // эксцентриситет
const WGS84_E2: f64 = WGS84_E * WGS84_E; // квадрат эксцентриситета
const UTM_K0: f64 = 0.9996; // масштабный коэффициент UTM

/// Координаты в системе UTM.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct UTM {
    /// Координата на восток (метры)
    pub easting: f64,
    /// Координата на север (метры)
    pub northing: f64,
    /// Номер зоны (1-60)
    pub zone: u8,
    /// Полушарие
    pub hemisphere: Hemisphere,
}

impl UTM {
    /// Конвертировать UTM координаты обратно в WGS84.
    ///
    /// # Примеры
    ///
    /// ```
    /// use coordinate_converter::{WGS84, UTM, Hemisphere};
    ///
    /// let utm = UTM {
    ///     easting: 413589.0,
    ///     northing: 6178456.0,
    ///     zone: 37,
    ///     hemisphere: Hemisphere::North,
    /// };
    /// let wgs = utm.to_wgs84();
    /// assert!((wgs.lat - 55.7558).abs() < 0.001);
    /// ```
    pub fn to_wgs84(&self) -> WGS84 {
        if !(1..=60).contains(&self.zone) {
            return WGS84 { lat: 0.0, lon: 0.0 };
        }

        // Центральный меридиан зоны в радианах
        let lon0 = ((self.zone as f64 - 1.0) * 6.0 - 180.0 + 3.0).to_radians();

        // Убираем ложное смещение
        let x = self.easting - 500000.0;
        let y = if matches!(self.hemisphere, Hemisphere::South) {
            self.northing - 10000000.0
        } else {
            self.northing
        };

        // Итеративное вычисление широты
        let mut lat = y / (WGS84_A * (1.0 - WGS84_E2 / 4.0 - 3.0 * WGS84_E2 * WGS84_E2 / 64.0 - 5.0 * WGS84_E2 * WGS84_E2 * WGS84_E2 / 256.0));
        
        for _ in 0..10 {
            let sin_lat = lat.sin();
            let m = WGS84_A * ((1.0 - WGS84_E2 / 4.0 - 3.0 * WGS84_E2 * WGS84_E2 / 64.0 - 5.0 * WGS84_E2 * WGS84_E2 * WGS84_E2 / 256.0) * lat
                - (3.0 * WGS84_E2 / 8.0 + 3.0 * WGS84_E2 * WGS84_E2 / 32.0 + 45.0 * WGS84_E2 * WGS84_E2 * WGS84_E2 / 1024.0) * (2.0 * lat).sin()
                + (15.0 * WGS84_E2 * WGS84_E2 / 256.0 + 45.0 * WGS84_E2 * WGS84_E2 * WGS84_E2 / 1024.0) * (4.0 * lat).sin()
                - (35.0 * WGS84_E2 * WGS84_E2 * WGS84_E2 / 3072.0) * (6.0 * lat).sin());
            
            lat = lat + (y / UTM_K0 - m) / (WGS84_A * (1.0 - WGS84_E2 * sin_lat * sin_lat).sqrt());
        }

        // Вычисление долготы
        let sin_lat = lat.sin();
        let cos_lat = lat.cos();
        let tan_lat = sin_lat / cos_lat;
        
        let n = WGS84_A / (1.0 - WGS84_E2 * sin_lat * sin_lat).sqrt();
        let t = tan_lat * tan_lat;
        let c = WGS84_E2 * cos_lat * cos_lat / (1.0 - WGS84_E2);
        
        let lon = lon0 + (x / (UTM_K0 * n) 
            - (1.0 + 2.0 * t + c) * (x / (UTM_K0 * n)).powi(3) / 6.0
            + (5.0 - 2.0 * c + 28.0 * t - 3.0 * c * c + 8.0 * WGS84_E2 + 24.0 * t * t) * (x / (UTM_K0 * n)).powi(5) / 120.0) / cos_lat;

        WGS84 {
            lat: lat.to_degrees(),
            lon: lon.to_degrees(),
        }
    }
}

/// Полушарие для UTM координат.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Hemisphere {
    North,
    South,
}