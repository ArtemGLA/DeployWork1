<script lang="ts">
  /**
   * WaypointMarker - массив точек и массив линий между ними.
   */
  import type { Mission } from './types';
  
  export let map: any;
  export let L: any = null;

  let waypointMarkers: any[] = [];
  let waypointLine: any = null;

  function clearWaypoints() {
    // удаление точек
    if (waypointMarkers && waypointMarkers.length) {
      waypointMarkers.forEach(marker => {
        if (marker && map) map.removeLayer(marker);
      });
      waypointMarkers = [];
    }
    
    // удаление линий
    if (waypointLine) {
      if (Array.isArray(waypointLine)) {
        waypointLine.forEach(line => {
          if (line && map) map.removeLayer(line);
        });
      } else if (map.removeLayer) {
        map.removeLayer(waypointLine);
      }
      waypointLine = null;
    }
  }

  export function createWaypoints(mission: Mission) {
    clearWaypoints();
    
    const points: [number, number][] = [];
    
    // цвет точек в зависимости от типа
    mission.waypoints.forEach((wp, index) => {
      let bgColor = '#0078ff';
      let symbol = `${index + 1}`;
      
      if (wp.type === 'takeoff' || wp.type === 'land') {
        bgColor = wp.type === 'takeoff' ? '#9b59b6' : '#e91e63';
        symbol = 'H';
      }
      
      const customIcon = L.divIcon({
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
          font-size: 14px;
        ">${symbol}</div>`,
        iconSize: [32, 32],
        popupAnchor: [0, -16]
      });

      // задание координат точкам
      const marker = L.marker([wp.lat, wp.lon], { icon: customIcon })
        .bindPopup(`Waypoint ${index + 1}${wp.type !== 'waypoint' ? ` (${wp.type})` : ''}`)
        .addTo(map);
      
      waypointMarkers.push(marker);
      points.push([wp.lat, wp.lon]);
    });
    
    // создание линий между каждой точкой
    if (points.length > 1) {
      const allLines = [];
      for (let i = 0; i < points.length; i++) {
        for (let j = i + 1; j < points.length; j++) {
          const line = L.polyline([points[i], points[j]], {
            color: 'blue',
            weight: 0.5,
            opacity: 1.0
          }).addTo(map);
          allLines.push(line);
        }
      }
      waypointLine = allLines;
    }
  }

  

</script>

<!-- Компонент не имеет шаблона, только логика -->