<script lang="ts">
  /**
   * DroneMarker - иконка дрона учитывающая положение и вращение, а также ошибку вебсокета.
   */
  import droneIconUrlGreen from './icon.png';
  import droneIconUrlRed from './iconRed.png';
  import type { DronePosition } from './types';
  
  export let L: any;
  export let map: any;
  export let center: [number, number];
  export let position: DronePosition | null = null;
  
  let droneMarker: any = null;

let droneIconGreen: any;
let droneIconRed: any;
  
  async function init() {
    await import('leaflet-rotatedmarker');
    
  droneIconGreen = L.icon({
    iconUrl: droneIconUrlGreen,
    iconSize: [40, 40],
    iconAnchor: [20, 20]
  });
  
  droneIconRed = L.icon({
    iconUrl: droneIconUrlRed,
    iconSize: [40, 40],
    iconAnchor: [20, 20]
  });
    
    droneMarker = L.marker([center[0], center[1]], { 
      icon: droneIconGreen,
      rotationAngle: 0,
      rotationOrigin: 'center center'
    }).addTo(map);
    
    if (position) setPosition(position);
  }
  
  export function setPosition(newPosition: DronePosition) {
    position = newPosition;
    if (droneMarker && position) {
      droneMarker.setLatLng([position.lat, position.lon]);
      droneMarker.setRotationAngle(position.heading);
    }
  }
  
  export function remove() {
    if (droneMarker && map) map.removeLayer(droneMarker);
  }

export function error() {
  if (droneMarker) {
    droneMarker.setIcon(droneIconRed);  // просто меняем иконку
  }
}

export function open() {
  if (droneMarker) {
    droneMarker.setIcon(droneIconGreen);  // просто меняем иконку
  }
}
  
  init();
</script>