/**
 * Tests for mission store.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { mission, missionStats, addWaypoint, removeWaypoint, updateWaypoint, moveWaypoint, newMission } from './mission';
import type { Waypoint } from '../types';

describe('Mission Store', () => {
  beforeEach(() => {
    newMission();
  });
  
  describe('addWaypoint', () => {
    it('should add a waypoint to the mission', () => {
      addWaypoint({ lat: 55.7558, lon: 37.6173, alt: 50, type: 16 });
      
      const m = get(mission);
      expect(m.waypoints.length).toBe(1);
      expect(m.waypoints[0].lat).toBe(55.7558);
    });
    
    it('should generate unique IDs', () => {
      addWaypoint({ lat: 55.75, lon: 37.61, alt: 50, type: 16 });
      addWaypoint({ lat: 55.76, lon: 37.62, alt: 50, type: 16 });
      
      const m = get(mission);
      expect(m.waypoints[0].id).not.toBe(m.waypoints[1].id);
    });
  });
  
  describe('removeWaypoint', () => {
    it('should remove a waypoint by id', () => {
      addWaypoint({ lat: 55.75, lon: 37.61, alt: 50, type: 16 });
      
      const m1 = get(mission);
      const wpId = m1.waypoints[0].id;
      
      removeWaypoint(wpId);
      
      const m2 = get(mission);
      expect(m2.waypoints.length).toBe(0);
    });
  });
  
  describe('updateWaypoint', () => {
    it('should update waypoint properties', () => {
      addWaypoint({ lat: 55.75, lon: 37.61, alt: 50, type: 16 });
      
      const m1 = get(mission);
      const wpId = m1.waypoints[0].id;
      
      updateWaypoint(wpId, { alt: 100 });
      
      const m2 = get(mission);
      expect(m2.waypoints[0].alt).toBe(100);
    });
  });
  
  describe('moveWaypoint', () => {
    it('should reorder waypoints', () => {
      addWaypoint({ lat: 55.75, lon: 37.61, alt: 50, type: 16 });
      addWaypoint({ lat: 55.76, lon: 37.62, alt: 50, type: 16 });
      addWaypoint({ lat: 55.77, lon: 37.63, alt: 50, type: 16 });
      
      const m1 = get(mission);
      const wp3Id = m1.waypoints[2].id;
      
      moveWaypoint(2, 0);
      
      const m2 = get(mission);
      expect(m2.waypoints[0].id).toBe(wp3Id);
    });
  });
  
  describe('missionStats', () => {
    it('should calculate distance', () => {
      addWaypoint({ lat: 55.7558, lon: 37.6173, alt: 50, type: 16 });
      addWaypoint({ lat: 55.7658, lon: 37.6173, alt: 50, type: 16 });
      
      const stats = get(missionStats);
      expect(stats.totalDistance).toBeGreaterThan(0);
    });
    
    it('should count waypoints', () => {
      addWaypoint({ lat: 55.75, lon: 37.61, alt: 50, type: 16 });
      addWaypoint({ lat: 55.76, lon: 37.62, alt: 50, type: 16 });
      
      const stats = get(missionStats);
      expect(stats.waypointCount).toBe(2);
    });
    
    it('should calculate min/max altitude', () => {
      addWaypoint({ lat: 55.75, lon: 37.61, alt: 30, type: 16 });
      addWaypoint({ lat: 55.76, lon: 37.62, alt: 100, type: 16 });
      addWaypoint({ lat: 55.77, lon: 37.63, alt: 50, type: 16 });
      
      const stats = get(missionStats);
      expect(stats.minAltitude).toBe(30);
      expect(stats.maxAltitude).toBe(100);
    });
  });
});
