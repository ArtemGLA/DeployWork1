export interface DronePosition {
  lat: number;
  lon: number;
  alt: number;
  heading: number;
  groundspeed: number;
  timestamp: number;
}

export interface Waypoint {
  id: number;
  lat: number;
  lon: number;
  alt: number;
  type: 'takeoff' | 'waypoint' | 'land' | 'rtl';
}

export interface Mission {
  name: string;
  waypoints: Waypoint[];
}

export interface StatusUpdate {
  armed: boolean;
  mode: string;
  battery: number;
  gpsStatus: 'no_fix' | '2d' | '3d' | 'dgps';
}

export type WebSocketMessageType = 'position' | 'mission' | 'status';

export interface WebSocketMessage<T = unknown> {
  type: WebSocketMessageType;
  data: T;
}

export interface MapConfig {
  center: [number, number];
  zoom: number;
  minZoom: number;
  maxZoom: number;
  tileUrl: string;
}

export const DEFAULT_MAP_CONFIG: MapConfig = {
  center: [55.7558, 37.6173],
  zoom: 15,
  minZoom: 3,
  maxZoom: 19,
  tileUrl: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
};
