<script lang="ts">
  /**
   * DroneMap - интерактивная карта с отображением дрона и траектории.
   */
import { onMount, onDestroy } from 'svelte';
import type { DronePosition, Mission, MapConfig } from './types';
import { DEFAULT_MAP_CONFIG } from './types';
import { DroneWebSocket } from './websocket';           // Вебсокет
  
  export let config: MapConfig = DEFAULT_MAP_CONFIG;
  export let mission: Mission | null = null;
  export let wsUrl: string = 'ws://localhost:8080';
  export let followDrone: boolean = true;
  
  let L: any = null; 
  let mapContainer: HTMLDivElement;
  let map: any = null;  // L.Map
  
  let dronePosition: DronePosition | null = null;
  let connected: boolean = false;
  let ws: DroneWebSocket | null = null;

  let droneMarker: any = null;
  let waypointMarkers: any = null;
  let trajectory: any = null;
  
  onMount(async () => {

    // Карта и leaflet
    await initMap();

    // Импорт компонентов
    const { DroneMarkerClass, TrajectoryClass, WaypointMarkerClass } = await importComponents();
  
    // Инициализация маркера
    droneMarker = new DroneMarkerClass({
      target: document.createElement('div'),
      props: { L, map, center: config.center, position: dronePosition }
    });

    // Инициализация точек и линий между ними
    waypointMarkers = new WaypointMarkerClass({
      target: document.createElement('div'),
      props: { L, map}
    });

    // Инициализация траектории
    trajectory = new TrajectoryClass({
      target: document.createElement('div'),
      props: { map, L}
    });

    // Создание подключения
    connectWebSocket();
    
  });
  
  // Уничтожение компонентов
  onDestroy(() => {
    ws?.close(); 

    droneMarker?.remove();     
  droneMarker?.$destroy();   
  
  trajectory?.clear();     
  trajectory?.$destroy();
  
  waypointMarkers?.clearWaypoints();
  waypointMarkers?.$destroy();

    map?.remove();
  });

  async function initMap() {
    L = await import('leaflet');
    map = L.map(mapContainer).setView(config.center, config.zoom);
    L.tileLayer(config.tileUrl).addTo(map);
  }

  async function importComponents() {
    const [{ default: DroneMarkerClass }, 
          { default: TrajectoryClass }, 
          { default: WaypointMarkerClass }] = await Promise.all([
      import('./DroneMarker.svelte'),
      import('./Trajectory.svelte'),
      import('./WaypointMarker.svelte')
    ]);
    
    return { DroneMarkerClass, TrajectoryClass, WaypointMarkerClass };
  }
  
  function connectWebSocket() {

    // Подключение WebSocket
    ws = new DroneWebSocket(wsUrl);

    ws.onOpen = () => {
      connected = true;
      droneMarker.open();
    };
    
    ws.onClose = () => {
      connected = false;
    };
    
    ws.onError = (error) => {
      console.error('WebSocket error:', error);
      connected = false;
      droneMarker.error();
    };
    
    ws.onPosition = (pos: DronePosition) => {
      updateDronePosition(pos);
    };
    
    ws.onMission = (m: Mission) => {
      updateWaypoints(m);
    };
    
    ws.connect();
  }
  
  function updateDronePosition(pos: DronePosition) {
  dronePosition = pos;
  droneMarker?.setPosition(pos);
  trajectory?.changeTrajectory(pos);

    if (followDrone && map) {
      map.setView([pos.lat, pos.lon], map.getZoom());
    }

  }

function updateWaypoints(m: Mission) {
  mission = m;
  waypointMarkers?.createWaypoints(mission);
}
  
  function centerOnDrone() {
    if (dronePosition && map) {
      map.setView([dronePosition.lat, dronePosition.lon], config.zoom);
    }
  }
  
  function toggleFollow() {
    followDrone = !followDrone;
  }
</script>

<div class="drone-map">
  <div class="map-container" bind:this={mapContainer}>
  </div>
  <div class="controls">
    <button on:click={centerOnDrone} title="Center on drone">
      ⌖
    </button>
    <button on:click={toggleFollow} class:active={followDrone} title="Follow drone">
      {followDrone ? '🔒' : '🔓'}
    </button>
  </div>
  
  <div class="status-bar">
    <span class="connection" class:connected>
      {connected ? '● Connected' : '○ Disconnected'}
    </span>
    
    {#if dronePosition}
      <span>Lat: {dronePosition.lat.toFixed(4)}</span>
      <span>Lon: {dronePosition.lon.toFixed(4)}</span>
      <span>Alt: {dronePosition.alt.toFixed(1)}m</span>
      <span>Speed: {dronePosition.groundspeed.toFixed(1)}m/s</span>
    {/if}
  </div>
</div>

<style>
  .drone-map {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 400px;
  }
  
  .map-container {
    width: 100%;
    height: 100%;
    background: #e0e0e0;
  }
  
  .controls {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  
  .controls button {
    width: 40px;
    height: 40px;
    border: none;
    border-radius: 4px;
    background: white;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    cursor: pointer;
    font-size: 1.2rem;
  }
  
  .controls button:hover {
    background: #f0f0f0;
  }
  
  .controls button.active {
    background: #4ade80;
  }
  
  .status-bar {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 8px 12px;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    font-size: 0.875rem;
    display: flex;
    gap: 1rem;
    z-index: 1000;
  }
  
  .connection {
    color: #f87171;
  }
  
  .connection.connected {
    color: #4ade80;
  }
</style>
