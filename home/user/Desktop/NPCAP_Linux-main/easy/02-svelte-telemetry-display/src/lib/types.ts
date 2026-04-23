export type FlightMode = 'STABILIZE' | 'GUIDED' | 'AUTO' | 'LAND' | 'RTL';

export interface TelemetryData {
  altitude: number;
  speed: number;
  battery: number;
  lat: number;
  lon: number;
  satellites: number;
  mode: FlightMode;
  armed: boolean;
  heading: number;
  verticalSpeed: number;
}

export interface GaugeProps {
  value: number;
  min?: number;
  max?: number;
  unit?: string;
  label?: string;
}

export function getAltitudeColor(altitude: number): string {
  if (altitude < 100) return 'var(--color-success)';
  if (altitude < 200) return 'var(--color-warning)';
  return 'var(--color-danger)';
}

export function getBatteryColor(percent: number): string {
  if (percent > 50) return 'var(--color-success)';
  if (percent > 20) return 'var(--color-warning)';
  return 'var(--color-danger)';
}

export function getGpsQuality(satellites: number): 'good' | 'medium' | 'poor' {
  if (satellites >= 10) return 'good';
  if (satellites >= 6) return 'medium';
  return 'poor';
}
