<script lang="ts">
  /**
   * Drone Dashboard - main page.
   * 
   * TODO: Add all dashboard components
   */
  
  import { onMount, onDestroy } from 'svelte';
  import { drones, selectedDrone, selectedDroneId } from '$lib/stores/drone';
  
  onMount(() => {
    drones.fetchAll();
    drones.connect();
  });
  
  onDestroy(() => {
    drones.disconnect();
  });
  
  async function handleArm() {
    if ($selectedDroneId) {
      await drones.sendCommand($selectedDroneId, { command: 'arm' });
    }
  }
  
  async function handleDisarm() {
    if ($selectedDroneId) {
      await drones.sendCommand($selectedDroneId, { command: 'disarm' });
    }
  }
  
  async function handleTakeoff() {
    if ($selectedDroneId) {
      await drones.sendCommand($selectedDroneId, { command: 'takeoff', altitude: 20 });
    }
  }
  
  async function handleLand() {
    if ($selectedDroneId) {
      await drones.sendCommand($selectedDroneId, { command: 'land' });
    }
  }
  
  async function handleRTL() {
    if ($selectedDroneId) {
      await drones.sendCommand($selectedDroneId, { command: 'rtl' });
    }
  }
</script>

<svelte:head>
  <title>Drone Dashboard</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

<div class="dashboard">
  <header>
    <h1>Drone Dashboard</h1>
    <div class="connection-status" class:connected={$selectedDrone?.connected}>
      {$selectedDrone?.connected ? '● Connected' : '○ Disconnected'}
    </div>
  </header>
  
  <main>
    <section class="map-section">
      <!-- TODO: Add DroneMap component -->
      <div class="map-placeholder">
        Map Component
        {#if $selectedDrone}
          <p>Position: {$selectedDrone.position.lat.toFixed(6)}, {$selectedDrone.position.lon.toFixed(6)}</p>
        {/if}
      </div>
    </section>
    
    <aside class="sidebar">
      <section class="telemetry-panel">
        <h2>Telemetry</h2>
        {#if $selectedDrone}
          <div class="telemetry-grid">
            <div class="telemetry-item">
              <span class="label">Mode</span>
              <span class="value">{$selectedDrone.mode}</span>
            </div>
            <div class="telemetry-item">
              <span class="label">Armed</span>
              <span class="value" class:armed={$selectedDrone.armed}>
                {$selectedDrone.armed ? 'YES' : 'NO'}
              </span>
            </div>
            <div class="telemetry-item">
              <span class="label">Altitude</span>
              <span class="value">{$selectedDrone.position.relative_alt.toFixed(1)} m</span>
            </div>
            <div class="telemetry-item">
              <span class="label">Speed</span>
              <span class="value">{$selectedDrone.velocity.groundspeed.toFixed(1)} m/s</span>
            </div>
            <div class="telemetry-item">
              <span class="label">Battery</span>
              <span class="value" class:low={$selectedDrone.battery.remaining < 20}>
                {$selectedDrone.battery.remaining}%
              </span>
            </div>
            <div class="telemetry-item">
              <span class="label">GPS</span>
              <span class="value">{$selectedDrone.gps.satellites} sats</span>
            </div>
          </div>
        {:else}
          <p class="no-data">No drone selected</p>
        {/if}
      </section>
      
      <section class="control-panel">
        <h2>Controls</h2>
        <div class="control-buttons">
          <button on:click={handleArm} class="btn-arm">ARM</button>
          <button on:click={handleDisarm} class="btn-disarm">DISARM</button>
          <button on:click={handleTakeoff}>TAKEOFF</button>
          <button on:click={handleLand}>LAND</button>
          <button on:click={handleRTL}>RTL</button>
        </div>
      </section>
      
      <section class="attitude-panel">
        <h2>Attitude</h2>
        {#if $selectedDrone}
          <div class="attitude-display">
            <div>Roll: {($selectedDrone.attitude.roll * 180 / Math.PI).toFixed(1)}°</div>
            <div>Pitch: {($selectedDrone.attitude.pitch * 180 / Math.PI).toFixed(1)}°</div>
            <div>Heading: {($selectedDrone.attitude.yaw * 180 / Math.PI).toFixed(0)}°</div>
          </div>
        {/if}
      </section>
    </aside>
  </main>
</div>

<style>
  :global(body) {
    margin: 0;
    font-family: system-ui, -apple-system, sans-serif;
    background: #0f172a;
    color: white;
  }
  
  .dashboard {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background: #1e293b;
    border-bottom: 1px solid #334155;
  }
  
  header h1 {
    margin: 0;
    font-size: 1.5rem;
  }
  
  .connection-status {
    color: #ef4444;
  }
  
  .connection-status.connected {
    color: #22c55e;
  }
  
  main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }
  
  .map-section {
    flex: 1;
    background: #1e293b;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .map-placeholder {
    color: #64748b;
    text-align: center;
  }
  
  .sidebar {
    width: 320px;
    background: #1e293b;
    border-left: 1px solid #334155;
    overflow-y: auto;
  }
  
  .sidebar section {
    padding: 1rem;
    border-bottom: 1px solid #334155;
  }
  
  .sidebar h2 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    color: #94a3b8;
    text-transform: uppercase;
  }
  
  .telemetry-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }
  
  .telemetry-item {
    background: #0f172a;
    padding: 0.75rem;
    border-radius: 8px;
  }
  
  .telemetry-item .label {
    display: block;
    font-size: 0.75rem;
    color: #64748b;
    margin-bottom: 0.25rem;
  }
  
  .telemetry-item .value {
    font-size: 1.25rem;
    font-weight: bold;
  }
  
  .telemetry-item .value.armed {
    color: #22c55e;
  }
  
  .telemetry-item .value.low {
    color: #ef4444;
  }
  
  .control-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }
  
  .control-buttons button {
    padding: 0.75rem;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    background: #334155;
    color: white;
  }
  
  .control-buttons button:hover {
    background: #475569;
  }
  
  .btn-arm {
    background: #22c55e !important;
    color: black !important;
  }
  
  .btn-disarm {
    background: #ef4444 !important;
  }
  
  .attitude-display {
    font-family: monospace;
    font-size: 1rem;
  }
  
  .attitude-display div {
    padding: 0.5rem 0;
    border-bottom: 1px solid #334155;
  }
  
  .no-data {
    color: #64748b;
    font-style: italic;
  }
</style>
