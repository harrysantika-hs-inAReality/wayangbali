import { Application, Container, UPDATE_PRIORITY } from 'pixi.js';
import type { PuppetRig } from '../puppet/PuppetRig';

export class PixiRenderer {
  private static readonly FRAME_MS = 1000 / 30;
  private readonly app = new Application();
  private readonly framing = new Container({ label: 'ViewportFraming' });
  private resizeObserver?: ResizeObserver;
  private puppets: readonly { puppet: PuppetRig; slot: 'left' | 'right' }[] = [];
  private update?: (deltaMS: number, timestamp: number) => void;
  private lastVisualFrame = -1;

  async init(host: HTMLElement): Promise<void> {
    await this.app.init({
      width: Math.max(1, host.clientWidth),
      height: Math.max(1, host.clientHeight),
      resolution: Math.min(window.devicePixelRatio || 1, 2),
      autoDensity: true,
      backgroundAlpha: 0,
      antialias: true,
      preference: 'webgl',
      autoStart: false,
      sharedTicker: false,
    });
    // Pixi 8's maxFPS gate integer-truncates elapsed milliseconds. At 30 FPS
    // that can reject a valid 33.33 ms frame and visibly undershoot the target.
    // Keep its single RAF-backed ticker, but gate update + render together with
    // drift correction instead of stacking another timer or RAF loop.
    this.app.ticker.maxFPS = 0;
    this.app.ticker.remove(this.app.render, this.app);
    this.app.ticker.add((ticker) => {
      const timestamp = ticker.lastTime + ticker.elapsedMS;
      if (this.lastVisualFrame < 0) this.lastVisualFrame = timestamp - PixiRenderer.FRAME_MS;
      const elapsed = timestamp - this.lastVisualFrame;
      if (elapsed < PixiRenderer.FRAME_MS) return;
      this.lastVisualFrame = timestamp - (elapsed % PixiRenderer.FRAME_MS);
      this.update?.(elapsed, timestamp);
      this.app.render();
    }, undefined, UPDATE_PRIORITY.HIGH);
    this.app.stage.addChild(this.framing);
    this.app.canvas.id = 'wayang-canvas';
    this.app.canvas.setAttribute('role', 'img');
    this.app.canvas.setAttribute('aria-label', 'Wayang Bali');
    host.appendChild(this.app.canvas);

    this.resizeObserver = new ResizeObserver(() => {
      this.app.renderer.resize(
        Math.max(1, host.clientWidth),
        Math.max(1, host.clientHeight),
        Math.min(window.devicePixelRatio || 1, 2),
      );
      this.fit();
      // The capped ticker performs rendering, including after resize.
    });
    this.resizeObserver.observe(host);
    document.addEventListener('visibilitychange', this.onVisibilityChange);
  }

  show(puppets: readonly { puppet: PuppetRig; slot: 'left' | 'right' }[]): void {
    if (puppets.length > 2) throw new Error('At most two active Wayang are allowed.');
    this.framing.removeChildren();
    this.puppets = puppets;
    for (const { puppet, slot } of puppets) {
      puppet.setFacing(slot === 'left' ? 'right' : 'left');
      this.framing.addChild(puppet.root);
    }
    this.fit();
    this.onVisibilityChange();
    if (!puppets.length) this.app.render();
  }

  get screen(): { width: number; height: number } {
    return this.app.screen;
  }

  setUpdate(update: (deltaMS: number, timestamp: number) => void): void {
    this.update = update;
  }

  getPuppetStagePosition(puppet: PuppetRig): { x: number; y: number } {
    return {
      x: this.framing.x + puppet.root.x * this.framing.scale.x,
      y: this.framing.y + puppet.root.y * this.framing.scale.y,
    };
  }

  stageToPuppetPosition(x: number, y: number, output: { x: number; y: number }): void {
    output.x = (x - this.framing.x) / this.framing.scale.x;
    output.y = (y - this.framing.y) / this.framing.scale.y;
  }

  destroy(): void {
    this.resizeObserver?.disconnect();
    document.removeEventListener('visibilitychange', this.onVisibilityChange);
    this.app.destroy({ removeView: true }, { children: true });
  }

  private readonly onVisibilityChange = (): void => {
    if (document.hidden || !this.puppets.length) {
      this.app.stop();
      this.lastVisualFrame = -1;
    }
    else this.app.start();
  };

  private fit(): void {
    const { width, height } = this.app.screen;
    for (const { puppet, slot } of this.puppets) {
      const definition = puppet.definition;
      const scale = Math.min(width * 0.62 / definition.canvas.width,
        height * 0.92 / definition.canvas.height) * definition.defaultScale;
      puppet.setScale(scale);
      // Preserve normalized placement on resize; initial placement follows slots.
      const previous = puppet.root.position;
      const oldWidth = this.lastWidth;
      const oldHeight = this.lastHeight;
      puppet.setPosition(oldWidth && previous.x ? previous.x / oldWidth * width : width * (slot === 'left' ? 0.35 : 0.65),
        oldHeight && previous.y ? previous.y / oldHeight * height : height * 0.7);
    }
    this.lastWidth = width;
    this.lastHeight = height;
  }
  private lastWidth = 0;
  private lastHeight = 0;
}
