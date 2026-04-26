/**
 * Tests for DroneMap component utilities.
 */

import { describe, it, expect } from 'vitest';
import type { DronePosition, Waypoint, Mission, MapConfig } from './types';

describe('DroneMap types', () => {
  it('should validate DronePosition structure', () => {
    const pos: DronePosition = {
      lat: 55.7558,
      lon: 37.6173,
      alt: 100,
      heading: 90,
      timestamp: Date.now()
    };
    
    expect(pos.lat).toBe(55.7558);
    expect(pos.lon).toBe(37.6173);
    expect(pos.alt).toBe(100);
    expect(pos.heading).toBe(90);
  });
  
  it('should validate Waypoint structure', () => {
    const wp: Waypoint = {
      id: 1,
      lat: 55.7558,
      lon: 37.6173,
      alt: 50,
      type: 'WAYPOINT'
    };
    
    expect(wp.id).toBe(1);
    expect(wp.type).toBe('WAYPOINT');
  });
  
  it('should validate Mission structure', () => {
    const mission: Mission = {
      id: 'test-mission',
      name: 'Test Mission',
      waypoints: [
        { id: 1, lat: 55.75, lon: 37.61, alt: 50, type: 'TAKEOFF' },
        { id: 2, lat: 55.76, lon: 37.62, alt: 50, type: 'WAYPOINT' },
        { id: 3, lat: 55.75, lon: 37.61, alt: 0, type: 'LAND' }
      ]
    };
    
    expect(mission.waypoints.length).toBe(3);
    expect(mission.waypoints[0].type).toBe('TAKEOFF');
    expect(mission.waypoints[2].type).toBe('LAND');
  });
  
  it('should validate MapConfig defaults', () => {
    const config: MapConfig = {
      center: [55.7558, 37.6173],
      zoom: 15,
      tileUrl: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    };
    
    expect(config.zoom).toBe(15);
    expect(config.center[0]).toBe(55.7558);
  });
});

describe('Trajectory calculation', () => {
  it('should calculate distance between points', () => {
    const toRad = (deg: number) => deg * Math.PI / 180;
    
    const haversine = (lat1: number, lon1: number, lat2: number, lon2: number) => {
      const R = 6371000;
      const dLat = toRad(lat2 - lat1);
      const dLon = toRad(lon2 - lon1);
      const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
      return R * c;
    };
    
    // Moscow to nearby point (~1.5 km)
    const distance = haversine(55.7558, 37.6173, 55.7658, 37.6173);
    expect(distance).toBeGreaterThan(1000);
    expect(distance).toBeLessThan(2000);
  });
});
