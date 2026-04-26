<script lang="ts">
  import { onMount } from 'svelte';
  import droneIconUrl from './icon.png';
  
  export let map: any;
  export let center: [number, number];
  export let droneMarker: any = null;
  
  let markerCreated = false;
  
  function createMarker() {
    if (!map || markerCreated) return;
    
    (async () => {
      const L = await import('leaflet');
      await import('leaflet-rotatedmarker');
      
      const droneIcon = L.icon({
        iconUrl: droneIconUrl,
        rotationOrigin: "center center",
        rotationAngle: 45,
        iconSize: [40, 40],
        iconAnchor: [20, 20]
      });
      
      droneMarker = L.marker(center, { icon: droneIcon }).addTo(map);
      markerCreated = true;
    })();
  }
  
  $: if (map) {
    createMarker();
  }
</script>