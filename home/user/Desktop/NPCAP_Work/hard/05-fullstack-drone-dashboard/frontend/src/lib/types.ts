export interface Position {
  lat: number;
  lon: number;
  alt: number;
  relative_alt: number;
}

export interface Attitude {
  roll: number;
  pitch: number;
  yaw: number;
}

export interface Velocity {
  vx: number;
  vy: number;
  vz: number;
  groundspeed: number;
}

export interface Battery {
  voltage: number;
  current: number;
  remaining: number;
}

export interface GpsStatus {
  fix_type: number;
  satellites: number;
}

export interface DroneState {
  id: number;
  name: string;
  connected: boolean;
  armed: boolean;
  mode: string;
  position: Position;
  attitude: Attitude;
  velocity: Velocity;
  battery: Battery;
  gps: GpsStatus;
  last_update: number;
}

export interface TelemetryUpdate {
  type: 'telemetry';
  drone_id: number;
  timestamp: number;
  data: DroneState;
}

export interface Alert {
  id: string;
  drone_id: number;
  level: 'info' | 'warning' | 'error';
  message: string;
  timestamp: number;
}

export type Command = 
  | { command: 'arm' }
  | { command: 'disarm' }
  | { command: 'takeoff'; altitude: number }
  | { command: 'land' }
  | { command: 'rtl' }
  | { command: 'set_mode'; mode: string }
  | { command: 'goto'; lat: number; lon: number; alt: number };
