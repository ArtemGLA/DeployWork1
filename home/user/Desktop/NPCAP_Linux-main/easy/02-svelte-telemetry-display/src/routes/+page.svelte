<script lang="ts">
  import TelemetryPanel from '../lib/TelemetryPanel.svelte';  // ← ИЗМЕНИТЕ ЗДЕСЬ
  import type { TelemetryData } from '../lib/types';          // ← И ЗДЕСЬ
  
  let telemetry: TelemetryData = {
    altitude: 150,
    speed: 12.5,
    battery: 85,
    lat: 55.7558,
    lon: 37.6173,
    satellites: 12,
    mode: 'AUTO',
    armed: true,
    heading: 90,
    verticalSpeed: 0.5
  };
  
  function simulateTelemetry() {
    setInterval(() => {
      telemetry = {
        ...telemetry,
        altitude: telemetry.altitude + (Math.random() - 0.5) * 2,
        speed: Math.max(0, telemetry.speed + (Math.random() - 0.5)),
        battery: Math.max(0, telemetry.battery - 0.01),
        lat: telemetry.lat + (Math.random() - 0.5) * 0.0001,
        lon: telemetry.lon + (Math.random() - 0.5) * 0.0001,
        satellites: Math.floor(Math.random() * 5) + 8,
        heading: (telemetry.heading + 1) % 360,
        verticalSpeed: (Math.random() - 0.5) * 2
      };
    }, 100);
  }
  
  let isSimulating = false;
  
  function toggleSimulation() {
    if (!isSimulating) {
      simulateTelemetry();
      isSimulating = true;
    }
  }

//Темная светлая тема
let darkTheme = true;  
function toggleTheme() {
  darkTheme = !darkTheme;
  if (darkTheme) {
    document.body.classList.remove('light-theme');
  } else {
    document.body.classList.add('light-theme');
  }
}

</script>

<main>
  <button class="theme-btn" on:click={toggleTheme}>
    {darkTheme ? '🌙' : '☀️'}
  </button>

  <h1>Telemetry Display Demo</h1>
  
  <TelemetryPanel data={telemetry} />
  
  <div class="controls">
    <button on:click={toggleSimulation} disabled={isSimulating}>
      {isSimulating ? 'Симуляция запущена' : 'Запустить симуляцию'}
    </button>
    
    <div class="sliders">
      <label>
        Altitude: {telemetry.altitude.toFixed(0)}m
        <input type="range" min="0" max="500" bind:value={telemetry.altitude} />
      </label>
      
      <label>
        Speed: {telemetry.speed.toFixed(1)}m/s
        <input type="range" min="0" max="30" step="0.1" bind:value={telemetry.speed} />
      </label>
      
      <label>
        Battery: {telemetry.battery.toFixed(1)}%
        <input type="range" min="0" max="100" step="0.1" bind:value={telemetry.battery} />
      </label>
      
      <label>
        Satellites: {telemetry.satellites}
        <input type="range" min="0" max="20" bind:value={telemetry.satellites} />
      </label>
    </div>
    
    <div class="mode-controls">
      <label>
        Mode:
        <select bind:value={telemetry.mode}>
          <option value="STABILIZE">STABILIZE</option>
          <option value="GUIDED">GUIDED</option>
          <option value="AUTO">AUTO</option>
          <option value="LAND">LAND</option>
          <option value="RTL">RTL</option>
        </select>
      </label>
      
      <label>
        <input type="checkbox" bind:checked={telemetry.armed} />
        Armed
      </label>
    </div>
  </div>
</main>

<style>
:global(body) {
  margin: 0;
  padding: 0;
  background: #0f0f23;
  min-height: 100vh;
  transition: background 0.2s;
}

:global(:root) {
  --bg-secondary: #1a1a2e;
  --bg-tertiary: #16213e;
  --text-primary: #ffffff;
  --text-secondary: #888888;
  --border-color: #333333;
  --color-success: #4ade80;
  --color-warning: #facc15;
  --color-danger: #f87171;
}

:global(body.light-theme) {
  background: #2a2a3e;
}

:global(body.light-theme) {
  --bg-secondary: #3a3a4e;
  --bg-tertiary: #35354a;
  --text-primary: #f0f0f0;
  --text-secondary: #c0c0c0;
  --border-color: #555555;
  --color-success: #4ade80;
  --color-warning: #facc15;
  --color-danger: #f87171;
}
  
  main {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
    color: white;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }
  
  h1 {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .controls {
    margin-top: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  button {
    padding: 0.75rem 1.5rem;
    background: var(--color-success);
    border: none;
    border-radius: 4px;
    color: black;
    font-weight: bold;
    cursor: pointer;
  }
  
  
  button:disabled {
    background: #666;
    cursor: not-allowed;
  }

  .theme-btn {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}
  
  .sliders {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .sliders label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }
  
  .sliders input[type="range"] {
    flex: 1;
  }
  
  .mode-controls {
    display: flex;
    gap: 1rem;
    align-items: center;
  }
  
  select {
    padding: 0.5rem;
    border-radius: 4px;
    background: var(--bg-tertiary);
    color: white;
    border: 1px solid var(--border-color);
  }
</style>