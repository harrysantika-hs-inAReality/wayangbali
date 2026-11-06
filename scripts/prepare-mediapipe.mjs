import { cp, mkdir } from 'node:fs/promises';

// Copy the runtime from the exact installed package, including SIMD fallbacks.
const source = new URL('../node_modules/@mediapipe/tasks-vision/wasm/', import.meta.url);
const destination = new URL('../public/mediapipe/wasm/', import.meta.url);
await mkdir(destination, { recursive: true });
await cp(source, destination, { recursive: true });
