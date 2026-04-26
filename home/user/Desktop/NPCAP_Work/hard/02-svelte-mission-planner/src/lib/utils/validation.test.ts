/**
 * Tests for mission validation.
 */

import { describe, it, expect } from 'vitest';
import { validateMission } from './validation';
import type { Mission, Waypoint, ValidationError } from '../types';

function createWaypoint(overrides: Partial<Waypoint> = {}): Waypoint {
  return {
    id: 'wp-1',
    seq: 0,
    lat: 55.7558,
    lon: 37.6173,
    alt: 50,
    type: 16, // NAV_WAYPOINT
    speed: 5,
    ...overrides
  };
}

function createMission(waypoints: Waypoint[]): Mission {
  return {
    id: 'mission-1',
    name: 'Test Mission',
    waypoints,
    createdAt: Date.now(),
    updatedAt: Date.now()
  };
}

describe('validateMission', () => {
  it('should pass for valid mission', () => {
    const mission = createMission([
      createWaypoint({ seq: 0, type: 22, alt: 0 }), // TAKEOFF
      createWaypoint({ seq: 1, type: 16, alt: 50 }), // WAYPOINT
      createWaypoint({ seq: 2, type: 21, alt: 0 })  // LAND
    ]);
    
    const errors = validateMission(mission);
    expect(errors.length).toBe(0);
  });
  
  it('should fail for empty mission', () => {
    const mission = createMission([]);
    
    const errors = validateMission(mission);
    expect(errors.length).toBeGreaterThan(0);
    expect(errors.some(e => e.message.toLowerCase().includes('waypoint'))).toBe(true);
  });
  
  it('should warn about missing takeoff', () => {
    const mission = createMission([
      createWaypoint({ seq: 0, type: 16 }), // Regular waypoint
      createWaypoint({ seq: 1, type: 21 })  // LAND
    ]);
    
    const errors = validateMission(mission);
    const hasWarning = errors.some(e => 
      e.level === 'warning' && e.message.toLowerCase().includes('takeoff')
    );
    expect(hasWarning).toBe(true);
  });
  
  it('should warn about missing land', () => {
    const mission = createMission([
      createWaypoint({ seq: 0, type: 22 }), // TAKEOFF
      createWaypoint({ seq: 1, type: 16 })  // Regular waypoint (no land)
    ]);
    
    const errors = validateMission(mission);
    const hasWarning = errors.some(e => 
      e.level === 'warning' && e.message.toLowerCase().includes('land')
    );
    expect(hasWarning).toBe(true);
  });
  
  it('should error for altitude out of range', () => {
    const mission = createMission([
      createWaypoint({ seq: 0, alt: 150 }) // Too high
    ]);
    
    const errors = validateMission(mission);
    const hasAltError = errors.some(e => 
      e.level === 'error' && e.message.toLowerCase().includes('altitude')
    );
    expect(hasAltError).toBe(true);
  });
  
  it('should error for invalid coordinates', () => {
    const mission = createMission([
      createWaypoint({ seq: 0, lat: 100, lon: 37 }) // Invalid lat
    ]);
    
    const errors = validateMission(mission);
    const hasCoordError = errors.some(e => 
      e.level === 'error' && e.message.toLowerCase().includes('coordinate')
    );
    expect(hasCoordError).toBe(true);
  });
});

describe('ValidationError', () => {
  it('should have correct structure', () => {
    const error: ValidationError = {
      waypointId: 'wp-1',
      field: 'altitude',
      message: 'Altitude exceeds maximum',
      level: 'error'
    };
    
    expect(error.level).toBe('error');
    expect(error.waypointId).toBe('wp-1');
  });
});
