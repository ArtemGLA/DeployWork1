export interface TelemetryData {
  altitude: number;
  speed: number;
  battery: number;
  lat: number;
  lon: number;
  satellites: number;
  mode: FlightMode;
  armed: boolean;
}

export type FlightMode = 'STABILIZE' | 'GUIDED' | 'AUTO' | 'LAND' | 'RTL';