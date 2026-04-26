<script lang="ts">
  /**
   * Mission Planner - главная страница.
   * 
   * TODO: Интегрируйте все компоненты
   */
  
  import { onMount } from 'svelte';
  import { mission, missionStats, loadMissionFromStorage, saveMissionToStorage } from '$lib/stores/mission';
  import { validateMission } from '$lib/utils/validation';
  import { exportToMAVLink, exportToQGC, exportToKML, downloadFile } from '$lib/utils/export';
  
  let validationResult = validateMission($mission);
  
  $: validationResult = validateMission($mission);
  
  onMount(() => {
    loadMissionFromStorage();
  });
  
  function handleNewMission() {
    if (confirm('Create new mission? Current mission will be lost.')) {
      mission.reset();
    }
  }
  
  function handleSave() {
    saveMissionToStorage();
    alert('Mission saved to local storage');
  }
  
  function handleExportMAVLink() {
    const content = exportToMAVLink($mission);
    downloadFile(content, `${$mission.name}.waypoints`, 'text/plain');
  }
  
  function handleExportQGC() {
    const content = JSON.stringify(exportToQGC($mission), null, 2);
    downloadFile(content, `${$mission.name}.plan`, 'application/json');
  }
  
  function handleExportKML() {
    const content = exportToKML($mission);
    downloadFile(content, `${$mission.name}.kml`, 'application/vnd.google-earth.kml+xml');
  }
  
  function handleAddWaypoint() {
    // TODO: Добавить waypoint в центре карты или по клику
    const lat = $mission.home.lat + (Math.random() - 0.5) * 0.01;
    const lon = $mission.home.lon + (Math.random() - 0.5) * 0.01;
    mission.addWaypoint(lat, lon, 50);
  }
</script>

<svelte:head>
  <title>Mission Planner</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

<main>
  <header class="toolbar">
    <div class="toolbar-group">
      <button on:click={handleNewMission}>New</button>
      <button on:click={handleSave}>Save</button>
      <button on:click={handleAddWaypoint}>Add Waypoint</button>
    </div>
    
    <div class="toolbar-group">
      <span class="mission-name">{$mission.name}</span>
    </div>
    
    <div class="toolbar-group">
      <button on:click={handleExportMAVLink}>Export MAVLink</button>
      <button on:click={handleExportQGC}>Export QGC</button>
      <button on:click={handleExportKML}>Export KML</button>
    </div>
  </header>
  
  <div class="content">
    <div class="map-area">
      <!-- TODO: Добавьте MapView компонент -->
      <div class="map-placeholder">
        <p>Map will be here</p>
        <p>Click to add waypoints</p>
      </div>
      
      <div class="altitude-profile">
        <!-- TODO: Добавьте AltitudeProfile компонент -->
        <p>Altitude Profile</p>
      </div>
    </div>
    
    <aside class="sidebar">
      <section class="panel mission-info">
        <h3>Mission Info</h3>
        <dl>
          <dt>Waypoints</dt>
          <dd>{$missionStats.waypointCount}</dd>
          
          <dt>Distance</dt>
          <dd>{($missionStats.totalDistance / 1000).toFixed(2)} km</dd>
          
          <dt>Est. Time</dt>
          <dd>{Math.ceil($missionStats.estimatedTime / 60)} min</dd>
          
          <dt>Max Alt</dt>
          <dd>{$missionStats.maxAltitude} m</dd>
        </dl>
      </section>
      
      <section class="panel waypoint-list">
        <h3>Waypoints</h3>
        
        {#if $mission.waypoints.length === 0}
          <p class="empty">No waypoints. Click on map to add.</p>
        {:else}
          <ul>
            {#each $mission.waypoints as wp, i (wp.id)}
              <li class="waypoint-item">
                <span class="index">{i + 1}</span>
                <span class="type">{wp.type}</span>
                <span class="alt">{wp.alt}m</span>
                <button class="delete" on:click={() => mission.removeWaypoint(wp.id)}>×</button>
              </li>
            {/each}
          </ul>
        {/if}
      </section>
      
      <section class="panel validation">
        <h3>Validation</h3>
        
        {#if validationResult.valid}
          <p class="valid">✓ Mission is valid</p>
        {:else}
          <ul class="errors">
            {#each validationResult.errors as error}
              <li class={error.severity}>{error.message}</li>
            {/each}
          </ul>
        {/if}
      </section>
    </aside>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: system-ui, -apple-system, sans-serif;
  }
  
  main {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  
  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 1rem;
    background: #1f2937;
    color: white;
  }
  
  .toolbar-group {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }
  
  .toolbar button {
    padding: 0.5rem 1rem;
    background: #374151;
    border: none;
    border-radius: 4px;
    color: white;
    cursor: pointer;
  }
  
  .toolbar button:hover {
    background: #4b5563;
  }
  
  .mission-name {
    font-weight: bold;
  }
  
  .content {
    display: flex;
    flex: 1;
    overflow: hidden;
  }
  
  .map-area {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .map-placeholder {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: #e5e7eb;
    color: #6b7280;
  }
  
  .altitude-profile {
    height: 120px;
    background: #f3f4f6;
    border-top: 1px solid #d1d5db;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6b7280;
  }
  
  .sidebar {
    width: 300px;
    background: #f9fafb;
    border-left: 1px solid #d1d5db;
    overflow-y: auto;
  }
  
  .panel {
    padding: 1rem;
    border-bottom: 1px solid #d1d5db;
  }
  
  .panel h3 {
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    color: #374151;
    text-transform: uppercase;
  }
  
  .mission-info dl {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.25rem;
    margin: 0;
  }
  
  .mission-info dt {
    color: #6b7280;
    font-size: 0.875rem;
  }
  
  .mission-info dd {
    margin: 0;
    font-weight: bold;
    text-align: right;
  }
  
  .waypoint-list ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .waypoint-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: white;
    border-radius: 4px;
    margin-bottom: 0.25rem;
  }
  
  .waypoint-item .index {
    width: 24px;
    height: 24px;
    background: #3b82f6;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
  }
  
  .waypoint-item .type {
    flex: 1;
    text-transform: capitalize;
  }
  
  .waypoint-item .alt {
    color: #6b7280;
    font-size: 0.875rem;
  }
  
  .waypoint-item .delete {
    width: 24px;
    height: 24px;
    border: none;
    background: #fee2e2;
    color: #dc2626;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .empty {
    color: #9ca3af;
    font-style: italic;
  }
  
  .validation .valid {
    color: #16a34a;
  }
  
  .validation .errors {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .validation .error {
    color: #dc2626;
    padding: 0.25rem 0;
  }
  
  .validation .warning {
    color: #d97706;
    padding: 0.25rem 0;
  }
</style>
