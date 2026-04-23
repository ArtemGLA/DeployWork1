<script lang="ts">

  export let altitude: number;
  export let color: string;
  
  let history: number[] = [];

  let lastAltitude = altitude;
  let arrow = " ";
  
  // Вычисление изменения высоты
  $: {
    arrow = altitude > lastAltitude ? '⬆' : altitude < lastAltitude ? '⬇' : '•';
    lastAltitude = altitude;
  }

  $: formattedAltitude = altitude.toFixed(0);

  // Сохранение истории изменений
  $: {
    let newHistory = [...history, altitude];
    if (newHistory.length > 100) {
      newHistory = newHistory.slice(-100);
    }
    history = newHistory;
  }

</script>

<div class="gauge altitude" style="--gauge-color: {color}">
  <span class="label">ALTITUDE</span>
  <span class="value">{formattedAltitude} м</span>
  <span class="arrow">{arrow}</span>

    <!-- График -->
  <div class="graph">
    <svg width="100%" height="60" style="display: block;">
      <!-- Линия скорости -->
      <polyline
        points={history.map((v, i) => {
          let x = (i / 99) * 200;
          let y = 60 - (v / 500) * 50;
          return `${x},${y}`;
        }).join(' ')}
        stroke="cyan"
        stroke-width="2"
        fill="none"
      />
    </svg>
  </div>

</div>

<style>

  .gauge {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
    background: var(--bg-tertiary, #16213e);
    border-radius: 8px;
    min-width: 100px;
  }
  
  
  .altitude {
    color: var(--gauge-color);
  }
  
  .label {
    font-size: 0.75rem;
    color: var(--text-secondary, #888);
    margin-bottom: 0.5rem;
  }
  
  .value {
    font-size: 1.5rem;
    font-weight: bold;
    animation: pulse 1.0s ease;
  }

  @keyframes pulse {
    0% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.2); opacity: 1; }
    100% { transform: scale(1); opacity: 0.5; }
  }

</style>