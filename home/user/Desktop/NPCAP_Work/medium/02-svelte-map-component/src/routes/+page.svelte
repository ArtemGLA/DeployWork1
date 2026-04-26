<script lang="ts">
  import DroneMap from '$lib/DroneMap.svelte';
  import type { Mission } from '$lib/types';
  
  const testMission: Mission = {
    name: "Test Mission",
    waypoints: [
      { id: 1, lat: 55.7558, lon: 37.6173, alt: 0, type: 'takeoff' },
      { id: 2, lat: 55.7608, lon: 37.6173, alt: 50, type: 'waypoint' },
      { id: 3, lat: 55.7558, lon: 37.6273, alt: 75, type: 'waypoint' },
      { id: 4, lat: 55.7508, lon: 37.6173, alt: 50, type: 'waypoint' },
      { id: 5, lat: 55.7558, lon: 37.6073, alt: 25, type: 'waypoint' },
      { id: 6, lat: 55.7558, lon: 37.6173, alt: 0, type: 'land' }
    ]
  };
</script>

<main>
  <h1>Drone Map Demo</h1>
  
  <p>
    Запустите mock сервер: <code>node mock/server.js</code>
  </p>
  
  <div class="map-wrapper">
    <DroneMap 
      mission={testMission}
      wsUrl="ws://localhost:8080"
    />
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: system-ui, -apple-system, sans-serif;
  }
  
  main {
    padding: 1rem;
  }
  
  h1 {
    margin-bottom: 1rem;
  }
  
  code {
    background: #f0f0f0;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: monospace;
  }
  
  .map-wrapper {
    width: 100%;
    height: 600px;
    border: 1px solid #ccc;
    border-radius: 8px;
    overflow: hidden;
  }
</style>
