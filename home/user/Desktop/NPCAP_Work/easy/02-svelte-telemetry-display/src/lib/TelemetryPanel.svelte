<script lang="ts">

  import type { TelemetryData } from './types';
  import { getAltitudeColor, getBatteryColor, getGpsQuality } from './types';
  import AltitudeGauge from './AltitudeGauge.svelte';
  import SpeedGauge from './SpeedGauge.svelte'
  import BatteryGauge from './BatteryGauge.svelte'
  
  export let data: TelemetryData;
  
  //Цвет высоты, батареи, качества связи
  $: altitudeColor = getAltitudeColor(data.altitude);
  $: batteryColor = getBatteryColor(data.battery);
  $: gpsQuality = getGpsQuality(data.satellites);

</script>

<div class="telemetry-panel">
  
<div><h2>TELEMETRY PANEL</h2> 
</div>
  
  <div class="gauges">

    <!-- Индикатор высоты -->
    <AltitudeGauge altitude={data.altitude} color={altitudeColor}/>
    
    <!-- Индикатор скорости -->
    <SpeedGauge speed={data.speed}/>
    
    <!-- Индикатор батареи -->
     <BatteryGauge color={batteryColor} battery={data.battery}/>
  
  </div>
  
  <!-- Местонахождение и спутники -->
  <div class="info">
    <div class="gps">
      GPS: {data.lat.toFixed(4)}, {data.lon.toFixed(4)}
      | Satellites: {data.satellites}
      | {gpsQuality}
    </div>
    
    <div class="status">
      Mode: {data.mode}
      | Armed: {data.armed ? '✓' : '✗'}
    </div>
  </div>
</div>

<style>
  .telemetry-panel {
    background: var(--bg-secondary, #1a1a2e);
    border-radius: 8px;
    padding: 1rem;
    color: var(--text-primary, #fff);
    font-family: 'Segoe UI', system-ui, sans-serif;
  }
  
  h2 {
    margin: 0 0 1rem 0;
    text-align: center;
    font-size: 1rem;
    color: var(--text-secondary, #888);
    border-bottom: 1px solid var(--border-color, #333);
    padding-bottom: 0.5rem;
  }
  
  .gauges {
    display: flex;
    gap: 1rem;
    justify-content: space-around;
    margin-bottom: 1rem;
  }

  .info {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: var(--text-secondary, #aaa);
  }
  
  .gps, .status {
    display: flex;
    justify-content: space-between;
  }

  .telemetry-panel {
    --color-success: #4ade80;
    --color-warning: #facc15;
    --color-danger: #f87171;
}

</style>
