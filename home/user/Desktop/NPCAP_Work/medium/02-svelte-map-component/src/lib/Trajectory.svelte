<script lang="ts">
  /**
   * Trajectory - разноцветная траектория прохождения дрона.
   */
  import type { DronePosition } from './types';
  
  export let map: any;
  export let L: any = null;

  const MAX_TRAJECTORY_POINTS = 1000;
  let trajectory: [number, number][] = [];
  let trajectorySegments: any[] = [];  

  export function changeTrajectory(position: DronePosition) {
    if (position == null) return;

    // задание координат массиву 2 чисел, 
    // проверка на наличие точек
    const newPoint: [number, number] = [position.lat, position.lon];
    const lastPoint = trajectory.length > 0 ? trajectory[trajectory.length - 1] : null;

    // заполнение точками массива точек
    trajectory.push(newPoint);
    if (trajectory.length > MAX_TRAJECTORY_POINTS) trajectory = trajectory.slice(-MAX_TRAJECTORY_POINTS);

    // задание цвета сегментам
    if (lastPoint && map) {
      const color = getColorByAltitude(position.alt || 0);
      const segment = L.polyline([lastPoint, newPoint], {
        color: color,
        weight: 4,      // Толщина линии
        opacity: 0.8
      }).addTo(map);
      trajectorySegments.push(segment);

      // Ограничиваем количество отрезков
      while (trajectorySegments.length > MAX_TRAJECTORY_POINTS) {
        const old = trajectorySegments.shift();
        if (old) map.removeLayer(old);
      }
    }
  }

  export function clear() {
    if (trajectorySegments && trajectorySegments.length) {
      trajectorySegments.forEach(segment => {
        if (segment && map) map.removeLayer(segment);
      });
      trajectorySegments = [];
    }
    trajectory = [];
  }

  function getColorByAltitude(alt: number): string {
  // высота расчитана от 0 до 1
  const t = Math.min(1, Math.max(0, alt / 100)); // от 0 до 1

  // синий некрасивый, я заюзал зеленый, желтый, красный
  if (t < 0.5) {
    // Зелёный (0 м) -> Жёлтый (50 м)
    const r = Math.floor(255 * t * 2);
    return `rgb(${r}, 255, 0)`;
  } else {
    // Жёлтый (50 м) -> Красный (100 м)
    const g = Math.floor(255 * (1 - (t - 0.5) * 2));
    return `rgb(255, ${g}, 0)`;
  }
}
</script>