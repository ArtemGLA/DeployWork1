export type WaypointType = 'takeoff' | 'waypoint' | 'loiter' | 'roi' | 'land' | 'rtl';

export interface Waypoint {
  id: string;
  type: WaypointType;
  lat: number;
  lon: number;
  alt: number;
  speed?: number;
  holdTime?: number;
  radius?: number;
  turns?: number;
  direction?: 'cw' | 'ccw';
}

export interface HomePosition {
  lat: number;
  lon: number;
  alt: number;
}

export interface Mission {
  id: string;
  name: string;
  description?: string;
  home: HomePosition;
  waypoints: Waypoint[];
  createdAt: number;
  updatedAt: number;
}

export interface MissionStats {
  waypointCount: number;
  totalDistance: number;
  estimatedTime: number;
  maxAltitude: number;
  minAltitude: number;
}

export interface ValidationError {
  waypointId?: string;
  field?: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

export const WAYPOINT_COLORS: Record<WaypointType, string> = {
  takeoff: '#4ade80',
  waypoint: '#3b82f6',
  loiter: '#f59e0b',
  roi: '#8b5cf6',
  land: '#ef4444',
  rtl: '#ec4899',
};

export const MAV_CMD: Record<WaypointType, number> = {
  takeoff: 22,
  waypoint: 16,
  loiter: 17,
  roi: 201,
  land: 21,
  rtl: 20,
};
