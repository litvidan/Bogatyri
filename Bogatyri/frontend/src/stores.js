import { writable, derived } from 'svelte/store';

// позиция
export const currentPosition = writable({ x: 0, y: 0 });

// маршрут
export const route = writable([]);

// маяки
export const beacons = writable([]);

// состояние системы
export const systemStatus = writable({
    isRecording: false,
    frequency: 1,
    isConnected: false
});

// рассчитанный маршрут в реальном времени
export const realTimePath = writable([]);

// производное состояние - последняя позиция
export const lastPosition = derived(
    realTimePath,
    $path => $path[$path.length - 1] || { x: 0, y: 0 }
);
