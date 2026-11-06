/** New camera frames drive inference independently of the Pixi render ticker. */
export class VideoFrameLoop {
  private active = false;
  private frameCallback?: number;
  private fallbackTimer?: number;
  private processedFrame = -1;
  private lastInference = -Infinity;
  private nextInference = 0;
  private interval: number;

  constructor(
    private readonly video: HTMLVideoElement,
    private readonly process: (timestamp: number) => void,
    private readonly onError: (error: unknown) => void,
    targetFPS = 20,
  ) {
    const fps = Number.isFinite(targetFPS) ? Math.max(1, Math.min(30, targetFPS)) : 20;
    this.interval = 1000 / fps;
  }

  start(): void {
    if (this.active || document.hidden) return;
    this.active = true;
    this.watchFrame();
  }

  setTargetFPS(targetFPS: number): void {
    const fps = Number.isFinite(targetFPS) ? Math.max(1, Math.min(30, targetFPS)) : 20;
    this.interval = 1000 / fps;
  }

  stop(): void {
    this.active = false;
    if (this.frameCallback !== undefined) this.video.cancelVideoFrameCallback(this.frameCallback);
    window.clearTimeout(this.fallbackTimer);
    this.frameCallback = this.fallbackTimer = undefined;
  }

  private watchFrame(): void {
    if (!this.active) return;
    if (typeof this.video.requestVideoFrameCallback === 'function') {
      this.frameCallback = this.video.requestVideoFrameCallback((_now, metadata) => {
        this.frameCallback = undefined;
        // presentedFrames is the cross-browser frame identity. Some WebKit
        // MediaStream implementations expose a mediaTime that stays at zero.
        this.onFrame(Number.isFinite(metadata.presentedFrames) ? metadata.presentedFrames : metadata.mediaTime);
        this.watchFrame();
      });
    } else {
      // Poll at no more than 30 Hz and reject unchanged video timestamps.
      this.fallbackTimer = window.setTimeout(() => {
        this.fallbackTimer = undefined;
        const quality = this.video.getVideoPlaybackQuality?.();
        const legacyVideo = this.video as HTMLVideoElement & { webkitDecodedFrameCount?: number };
        // Android exposes totalVideoFrames, older Safari exposes the webkit
        // counter, and currentTime remains the final compatibility fallback.
        this.onFrame(quality?.totalVideoFrames || legacyVideo.webkitDecodedFrameCount || this.video.currentTime);
        this.watchFrame();
      }, 1000 / 30);
    }
  }

  private onFrame(mediaTime: number): void {
    if (!this.active || document.hidden || this.video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return;
    // A live MediaStream can report paused inconsistently on WebKit while it is
    // still producing frames. Frame readiness and identity are sufficient.
    if (this.video.ended || !Number.isFinite(mediaTime) || mediaTime === this.processedFrame) return;
    const now = performance.now();
    if (now < this.nextInference || now - this.lastInference < 1000 / 30) return;
    this.processedFrame = mediaTime;
    this.lastInference = now;
    // Carry the 20 FPS schedule across camera callbacks instead of waiting a
    // fresh 50 ms each time (which would halve a 24 FPS camera to 12 FPS).
    // The separate 30 FPS guard above forbids rapid catch-up inferences.
    this.nextInference = Math.max(this.nextInference + this.interval, now);
    try {
      // Infer synchronously inside the fresh-frame callback so a deferred read
      // cannot accidentally consume the next frame before its own callback.
      this.process(now);
    } catch (error) {
      this.stop();
      this.onError(error);
    }
  }
}
