#!/usr/bin/env node
/**
 * Mock WebSocket сервер для тестирования DroneMap компонента.
 * 
 * Симулирует движение дрона по круговой траектории.
 */

const WebSocket = require('ws');

const PORT = process.argv[2] ? parseInt(process.argv[2]) : 8080;

const wss = new WebSocket.Server({ port: PORT });

console.log(`Mock drone server started on ws://localhost:${PORT}`);

// Начальная позиция (Москва)
const HOME = { lat: 55.7558, lon: 37.6173 };
const RADIUS = 0.005;  // ~500м
const ALTITUDE = 50;

let angle = 0;
let time = 0;

function generatePosition() {
  // Круговое движение вокруг HOME
  const lat = HOME.lat + RADIUS * Math.cos(angle);
  const lon = HOME.lon + RADIUS * Math.sin(angle) * 1.5;  // Коррекция для долготы
  
  // Высота с небольшими колебаниями
  const alt = ALTITUDE + Math.sin(time * 0.5) * 10;
  
  // Направление (касательная к окружности)
  const heading = (Math.atan2(Math.cos(angle), -Math.sin(angle)) * 180 / Math.PI + 360) % 360;
  
  // Скорость
  const groundspeed = 8 + Math.sin(time) * 2;
  
  angle += 0.02;
  time += 0.1;
  
  return {
    lat,
    lon,
    alt,
    heading: Math.round(heading),
    groundspeed: Math.round(groundspeed * 10) / 10,
    timestamp: Date.now()
  };
}

const mission = {
  name: "Test Mission",
  waypoints: [
    { id: 1, lat: HOME.lat, lon: HOME.lon, alt: 0, type: 'takeoff' },
    { id: 2, lat: HOME.lat + RADIUS, lon: HOME.lon, alt: 50, type: 'waypoint' },
    { id: 3, lat: HOME.lat, lon: HOME.lon + RADIUS * 1.5, alt: 75, type: 'waypoint' },
    { id: 4, lat: HOME.lat - RADIUS, lon: HOME.lon, alt: 50, type: 'waypoint' },
    { id: 5, lat: HOME.lat, lon: HOME.lon - RADIUS * 1.5, alt: 25, type: 'waypoint' },
    { id: 6, lat: HOME.lat, lon: HOME.lon, alt: 0, type: 'land' }
  ]
};

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // Отправить миссию при подключении
  ws.send(JSON.stringify({
    type: 'mission',
    data: mission
  }));
  
  // Отправлять позицию каждые 100мс
  const interval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'position',
        data: generatePosition()
      }));
    }
  }, 100);
  
  ws.on('close', () => {
    console.log('Client disconnected');
    clearInterval(interval);
  });
  
  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
    clearInterval(interval);
  });
});

console.log('Press Ctrl+C to stop');
