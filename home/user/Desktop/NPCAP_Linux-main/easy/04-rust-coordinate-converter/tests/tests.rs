const EARTH_RADIUS: f64 = 6371000.0;
use std::f64::consts::PI;
use coordinate_converter::{WGS84, Hemisphere, CoordinateError};

#[test]
fn test_wgs84_creation() {
    let coord = WGS84::new(55.7558, 37.6173).unwrap();
    assert!((coord.lat - 55.7558).abs() < 1e-6);
    assert!((coord.lon - 37.6173).abs() < 1e-6);
}

#[test]
fn test_wgs84_invalid_lat() {
    let result = WGS84::new(95.0, 37.6173);
    assert!(result.is_err());
}

#[test]
fn test_wgs84_invalid_lon() {
    let result = WGS84::new(55.0, 200.0);
    assert!(result.is_err());
}

#[test]
fn test_distance_same_point() {
    let coord1 = WGS84::new(55.7558, 37.6173).unwrap();
    let coord2 = WGS84::new(55.7558, 37.6173).unwrap();
    
    let distance = coord1.distance_to(&coord2);
    assert!(distance < 1.0); // Less than 1 meter
}

#[test]
fn test_distance_known_points() {
    // Moscow to Saint Petersburg: ~634 km
    let moscow = WGS84::new(55.7558, 37.6173).unwrap();
    let spb = WGS84::new(59.9343, 30.3351).unwrap();
    
    let distance = moscow.distance_to(&spb);
    assert!(distance > 600_000.0 && distance < 700_000.0);
}

#[test]
fn test_bearing_east() {
    let point1 = WGS84::new(55.0, 37.0).unwrap();
    let point2 = WGS84::new(55.0, 38.0).unwrap(); // Due east
    
    let bearing = point1.bearing_to(&point2);
    assert!(bearing > 85.0 && bearing < 95.0); // Near 90 degrees
}

#[test]
fn test_utm_zone_moscow() {
    let moscow = WGS84::new(55.7558, 37.6173).unwrap();
    let utm = moscow.to_utm();
    
    assert_eq!(utm.zone, 37);
    assert_eq!(utm.hemisphere, Hemisphere::North);
}

#[test]
fn test_utm_roundtrip() {
    let original = WGS84::new(55.7558, 37.6173).unwrap();
    let utm = original.to_utm();
    let converted = utm.to_wgs84();
    
    assert!((original.lat - converted.lat).abs() < 0.0001);
    assert!((original.lon - converted.lon).abs() < 0.0001);
}

    #[test]
    fn test_wgs84_new_valid() {
        let point = WGS84::new(55.7558, 37.6173);
        assert!(point.is_ok());
    }

    #[test]
    fn test_wgs84_new_invalid_lat() {
        let point = WGS84::new(91.0, 0.0);
        assert!(matches!(point, Err(CoordinateError::InvalidLatitude(_))));
    }

    #[test]
    fn test_wgs84_new_invalid_lon() {
        let point = WGS84::new(0.0, 181.0);
        assert!(matches!(point, Err(CoordinateError::InvalidLongitude(_))));
    }

    #[test]
    fn test_utm_zone_calculation() {
        // Москва должна быть в зоне 37
        let moscow = WGS84::new(55.7558, 37.6173).unwrap();
        let utm = moscow.to_utm();
        assert_eq!(utm.zone, 37);
        assert_eq!(utm.hemisphere, Hemisphere::North);
        
        // Проверка приблизительных значений для Москвы
        assert!((utm.easting - 413589.0).abs() < 1000.0);
        assert!((utm.northing - 6178456.0).abs() < 1000.0);
    }

    #[test]
    fn test_utm_zone_south() {
        // Сидней (южное полушарие)
        let sydney = WGS84::new(-33.8688, 151.2093).unwrap();
        let utm = sydney.to_utm();
        assert_eq!(utm.zone, 56);
        assert_eq!(utm.hemisphere, Hemisphere::South);
        assert!(utm.northing > 6000000.0);
    }

    #[test]
    fn test_distance_moscow_spb() {
        let moscow = WGS84::new(55.7558, 37.6173).unwrap();
        let spb = WGS84::new(59.9343, 30.3351).unwrap();
        let distance = moscow.distance_to(&spb);
        // Примерно 635 км, допуск 5%
        assert!(distance > 600_000.0);
        assert!(distance < 670_000.0);
    }

    #[test]
    fn test_distance_known() {
        // Расстояние от экватора до полюса должно быть ~1/4 окружности
        let eq = WGS84::new(0.0, 0.0).unwrap();
        let pole = WGS84::new(90.0, 0.0).unwrap();
        let distance = eq.distance_to(&pole);
        let expected = EARTH_RADIUS * PI / 2.0;
        assert!((distance - expected).abs() < 1000.0);
    }

    #[test]
    fn test_bearing_north() {
        let point1 = WGS84::new(50.0, 0.0).unwrap();
        let point2 = WGS84::new(51.0, 0.0).unwrap();
        let bearing = point1.bearing_to(&point2);
        // Направление на север должно быть ~0°
        assert!(bearing < 1.0 || bearing > 359.0);
    }

    #[test]
    fn test_bearing_south() {
        let point1 = WGS84::new(51.0, 0.0).unwrap();
        let point2 = WGS84::new(50.0, 0.0).unwrap();
        let bearing = point1.bearing_to(&point2);
        // Направление на юг должно быть ~180°
        assert!(bearing > 179.0 && bearing < 181.0);
    }

    #[test]
    fn test_bearing_west() {
        let point1 = WGS84::new(0.0, 1.0).unwrap();
        let point2 = WGS84::new(0.0, 0.0).unwrap();
        let bearing = point1.bearing_to(&point2);
        // Направление на запад должно быть ~270°
        assert!(bearing > 269.0 && bearing < 271.0);
    }

    #[test]
    fn test_utm_to_wgs84_roundtrip() {
        // Тест обратного преобразования для Москвы
        let original = WGS84::new(55.7558, 37.6173).unwrap();
        let utm = original.to_utm();
        let converted = utm.to_wgs84();
        
        assert!((converted.lat - original.lat).abs() < 0.001);
        assert!((converted.lon - original.lon).abs() < 0.001);
    }

    #[test]
    fn test_utm_to_wgs84_roundtrip_south() {
        // Тест обратного преобразования для Сиднея
        let original = WGS84::new(-33.8688, 151.2093).unwrap();
        let utm = original.to_utm();
        let converted = utm.to_wgs84();
        
        assert!((converted.lat - original.lat).abs() < 0.001);
        assert!((converted.lon - original.lon).abs() < 0.001);
    }

    #[test]
    fn test_edge_cases() {
        // Тест на границах зон
        let point = WGS84::new(0.0, 179.9).unwrap();
        let utm = point.to_utm();
        assert_eq!(utm.zone, 60);
        
        let point2 = WGS84::new(0.0, -179.9).unwrap();
        let utm2 = point2.to_utm();
        assert_eq!(utm2.zone, 1);
    }
