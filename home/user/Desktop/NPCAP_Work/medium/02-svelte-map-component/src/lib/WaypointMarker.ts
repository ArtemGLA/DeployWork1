import type { Waypoint } from './types';

export function createWaypointMarkers(map: any, waypoints: Waypoint[]) {
  const markers: any[] = [];
  const points: [number, number][] = [];
  
  waypoints.forEach((wp, index) => {
    let bgColor = '#0078ff';
    let symbol = `${index + 1}`;
    let borderColor = 'white';
    
    if (wp.type === 'takeoff') {
      bgColor = '#9b59b6';
      symbol = 'H';
      borderColor = '#ffd700';
    } else if (wp.type === 'land') {
      bgColor = '#e91e63';
      symbol = 'H';
      borderColor = '#ffd700';
    }
    
    const customIcon = (L as any).divIcon({
      className: 'custom-waypoint-marker',
      html: `<div style="
        background-color: ${bgColor};
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: ${wp.type === 'waypoint' ? '14px' : '18px'};
        border: 2px solid ${borderColor};
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      ">${symbol}</div>`,
      iconSize: [32, 32],
      popupAnchor: [0, -16]
    });

    const marker = (L as any).marker([wp.lat, wp.lon], { icon: customIcon })
      .bindPopup(`Waypoint ${index + 1}`)
      .addTo(map);
    
    markers.push(marker);
    points.push([wp.lat, wp.lon]);
  });
  
  // Создаем линии
  let lines: any[] = [];
  if (points.length > 1) {
    for (let i = 0; i < points.length; i++) {
      for (let j = i + 1; j < points.length; j++) {
        const line = (L as any).polyline([points[i], points[j]], {
          color: 'blue',
          weight: 0.5,
          opacity: 1.0
        }).addTo(map);
        lines.push(line);
      }
    }
  }
  
  // Возвращаем функцию для очистки
  return {
    markers,
    lines,
    clear() {
      markers.forEach(m => map.removeLayer(m));
      lines.forEach(l => map.removeLayer(l));
    }
  };
}