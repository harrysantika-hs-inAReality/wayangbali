import './style.css';
import { GameApp } from './app/GameApp';
import { PixiRenderer } from './rendering/PixiRenderer';

const host = document.querySelector<HTMLElement>('#app');
const video = document.querySelector<HTMLVideoElement>('#camera-preview');
const ui = document.querySelector<HTMLElement>('#ui');
if (!host || !video || !ui) throw new Error('Missing application elements.');
const renderer = new PixiRenderer();
let game: GameApp | undefined;
let disposed = false;
let initialized = false;
void renderer.init(host).then(() => {
  initialized = true;
  if (disposed) { renderer.destroy(); initialized = false; return; }
  game = new GameApp(renderer, video, ui);
}).catch((error: unknown) => {
  console.error('Unable to initialize Wayang:', error);
  ui.textContent = 'Aplikasi tidak dapat dimuat. Silakan muat ulang halaman.';
});
if (import.meta.hot) {
  import.meta.hot.accept(() => window.location.reload());
  import.meta.hot.dispose(() => {
    disposed = true;
    void (game?.destroy() ?? Promise.resolve()).finally(() => {
      if (initialized) { renderer.destroy(); initialized = false; }
    });
  });
}
