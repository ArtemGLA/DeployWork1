/**
 * Tests for mission export functions.
 */

import { describe, it, expect } from 'vitest';
import { exportToMAVLink, exportToQGC, exportToKML } from './export';
import type { Mission, Waypoint } from '../types';

function createTestMission(): Mission {
  return {
    id: 'test-mission',
    name: 'Test Flight',
    waypoints: [
      {
        id: 'wp-1',
        seq: 0,
        lat: 55.7558,
        lon: 37.6173,
        alt: 0,
        type: 22, // TAKEOFF
        speed: 5
      },
      {
        id: 'wp-2',
        seq: 1,
        lat: 55.7568,
        lon: 37.6183,
        alt: 50,
        type: 16, // WAYPOINT
        speed: 10
      },
      {
        id: 'wp-3',
        seq: 2,
        lat: 55.7578,
        lon: 37.6173,
        alt: 50,
        type: 16,
        speed: 10
      },
      {
        id: 'wp-4',
        seq: 3,
        lat: 55.7558,
        lon: 37.6173,
        alt: 0,
        type: 21, // LAND
        speed: 5
      }
    ],
    createdAt: Date.now(),
    updatedAt: Date.now()
  };
}

describe('exportToMAVLink', () => {
  it('should export mission in MAVLink format', () => {
    const mission = createTestMission();
    const result = exportToMAVLink(mission);
    
    expect(result).toContain('QGC WPL 110');
    expect(result.split('\n').length).toBeGreaterThan(1);
  });
  
  it('should include all waypoints', () => {
    const mission = createTestMission();
    const result = exportToMAVLink(mission);
    const lines = result.trim().split('\n');
    
    // Header + waypoints
    expect(lines.length).toBe(1 + mission.waypoints.length);
  });
  
  it('should use correct command IDs', () => {
    const mission = createTestMission();
    const result = exportToMAVLink(mission);
    
    expect(result).toContain('22'); // TAKEOFF
    expect(result).toContain('16'); // WAYPOINT
    expect(result).toContain('21'); // LAND
  });
});

describe('exportToQGC', () => {
  it('should export mission as JSON', () => {
    const mission = createTestMission();
    const result = exportToQGC(mission);
    
    const parsed = JSON.parse(result);
    expect(parsed).toHaveProperty('mission');
    expect(parsed).toHaveProperty('geoFence');
    expect(parsed).toHaveProperty('rallyPoints');
  });
  
  it('should include mission items', () => {
    const mission = createTestMission();
    const result = exportToQGC(mission);
    
    const parsed = JSON.parse(result);
    expect(parsed.mission.items.length).toBe(mission.waypoints.length);
  });
});

describe('exportToKML', () => {
  it('should export mission as KML', () => {
    const mission = createTestMission();
    const result = exportToKML(mission);
    
    expect(result).toContain('<?xml version="1.0"');
    expect(result).toContain('<kml');
    expect(result).toContain('</kml>');
  });
  
  it('should include placemark for each waypoint', () => {
    const mission = createTestMission();
    const result = exportToKML(mission);
    
    const placemarkCount = (result.match(/<Placemark>/g) || []).length;
    expect(placemarkCount).toBe(mission.waypoints.length);
  });
  
  it('should include coordinates', () => {
    const mission = createTestMission();
    const result = exportToKML(mission);
    
    expect(result).toContain('55.7558');
    expect(result).toContain('37.6173');
  });
  
  it('should include mission name', () => {
    const mission = createTestMission();
    const result = exportToKML(mission);
    
    expect(result).toContain('Test Flight');
  });
});
