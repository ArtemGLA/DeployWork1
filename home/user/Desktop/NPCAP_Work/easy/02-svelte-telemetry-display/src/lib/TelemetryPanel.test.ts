/**
 * Tests for TelemetryPanel component.
 */

import { describe, it, expect } from 'vitest';
import { getBatteryColor, getGpsQualityText, type TelemetryData } from './types';

describe('TelemetryPanel utilities', () => {
  describe('getBatteryColor', () => {
    it('should return red for low battery', () => {
      expect(getBatteryColor(15)).toBe('#ef4444');
      expect(getBatteryColor(5)).toBe('#ef4444');
    });
    
    it('should return yellow for medium battery', () => {
      expect(getBatteryColor(35)).toBe('#eab308');
      expect(getBatteryColor(25)).toBe('#eab308');
    });
    
    it('should return green for high battery', () => {
      expect(getBatteryColor(80)).toBe('#22c55e');
      expect(getBatteryColor(100)).toBe('#22c55e');
    });
  });
  
  describe('getGpsQualityText', () => {
    it('should return No Fix for 0-1', () => {
      expect(getGpsQualityText(0)).toBe('No Fix');
      expect(getGpsQualityText(1)).toBe('No Fix');
    });
    
    it('should return 2D for fix type 2', () => {
      expect(getGpsQualityText(2)).toBe('2D');
    });
    
    it('should return 3D for fix type 3', () => {
      expect(getGpsQualityText(3)).toBe('3D');
    });
    
    it('should return DGPS for fix type 4', () => {
      expect(getGpsQualityText(4)).toBe('DGPS');
    });
    
    it('should return RTK for fix type 5-6', () => {
      expect(getGpsQualityText(5)).toBe('RTK');
      expect(getGpsQualityText(6)).toBe('RTK');
    });
  });
});

describe('TelemetryData interface', () => {
  it('should accept valid telemetry data', () => {
    const data: TelemetryData = {
      timestamp: Date.now(),
      position: { lat: 55.7558, lon: 37.6173, alt: 100.0 },
      attitude: { roll: 0.0, pitch: 0.0, yaw: 90.0 },
      speed: { ground: 10.0, air: 12.0, vertical: 0.5 },
      battery: { voltage: 12.5, remaining: 85 },
      gps: { fix: 3, satellites: 12 },
      mode: 'GUIDED',
      armed: true
    };
    
    expect(data.position.lat).toBe(55.7558);
    expect(data.armed).toBe(true);
    expect(data.mode).toBe('GUIDED');
  });
});
