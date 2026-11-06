import { CameraManager } from '../camera/CameraManager';
import { VideoFrameLoop } from '../camera/VideoFrameLoop';
import type { HandLandmarkerResult } from '@mediapipe/tasks-vision';
import type { HandLandmarkerManager } from '../vision/HandLandmarkerManager';

export class CameraSession {
  private readonly camera: CameraManager;
  private vision?: HandLandmarkerManager;
  private loop?: VideoFrameLoop;
  private request?: AbortController;
  private state: 'idle' | 'starting' | 'running' | 'disposed' = 'idle';
  private inferenceAverage = 0;
  private measuredFrames = 0;
  private lastAdjustment = 0;
  private performanceFPS = 20;

  constructor(
    private readonly video: HTMLVideoElement,
    private readonly callbacks: {
      result: (result: HandLandmarkerResult, timestamp: number) => void;
      status: (message: string) => void;
      /** Startup progress, 0..100 overall, with a short user-facing step label. */
      progress: (percent: number, label: string) => void;
      ready: () => void;
      pause: () => void;
      error: (message: string) => void;
    },
  ) {
    this.camera = new CameraManager(video, () => this.fail('Kamera terputus. Silakan coba lagi.'));
    document.addEventListener('visibilitychange', this.onVisibilityChange);
    window.addEventListener('pagehide', this.onPageHide);
  }

  readonly start = async (): Promise<void> => {
    if (this.state !== 'idle') return;
    this.state = 'starting';
    const request = new AbortController();
    this.request = request;
    this.callbacks.progress(35, 'Menyalakan kamera. Izinkan akses kamera bila diminta.');
    try {
      await this.camera.start(request.signal);
      request.signal.throwIfAborted();
      this.callbacks.progress(50, 'Memuat pelacak tangan…');
      // Load vision code and its local assets only after the user starts camera.
      const { HandLandmarkerManager } = await import('../vision/HandLandmarkerManager');
      request.signal.throwIfAborted();
      this.vision = await HandLandmarkerManager.create(request.signal, fraction => {
        if (request.signal.aborted) return;
        this.callbacks.progress(52 + fraction * 38, fraction < 1 ? 'Mengunduh model pelacak tangan…' : 'Menyiapkan pelacak tangan…');
      });
      request.signal.throwIfAborted();
      this.loop = new VideoFrameLoop(
        this.video,
        (timestamp) => {
          const before = performance.now();
          const result = this.vision!.detect(this.video, timestamp);
          const duration = performance.now() - before;
          this.inferenceAverage = this.measuredFrames++ ? this.inferenceAverage * 0.9 + duration * 0.1 : duration;
          // Warm up before adapting, then use hysteresis to avoid oscillation.
          if (this.measuredFrames >= 20 && timestamp - this.lastAdjustment >= 2000) {
            if (this.inferenceAverage > 55) this.performanceFPS = 12;
            else if (this.inferenceAverage > 35) this.performanceFPS = 15;
            else if (this.inferenceAverage < 25) this.performanceFPS = 20;
            this.lastAdjustment = timestamp;
          }
          this.loop?.setTargetFPS(result.landmarks.length ? this.performanceFPS : Math.min(12, this.performanceFPS));
          this.callbacks.result(result, timestamp);
        },
        (error) => {
          console.error('Hand tracking stopped:', error);
          this.fail('Pelacakan tangan berhenti. Silakan mulai kamera lagi.');
        },
        20,
      );
      this.state = 'running';
      this.callbacks.progress(100, 'Panggung siap.');
      this.callbacks.ready();
      this.onVisibilityChange();
    } catch (error) {
      if (request.signal.aborted) return;
      console.error('Camera session could not start:', error);
      this.fail(error instanceof Error ? error.message : 'Kamera tidak dapat dimulai. Silakan coba lagi.');
    }
  };

  private readonly onVisibilityChange = (): void => {
    if (document.hidden) {
      this.loop?.stop();
      this.callbacks.pause();
    } else if (this.state === 'running') {
      // Some mobile browsers pause the video when backgrounded.
      const request = this.request;
      void this.video.play().then(() => {
        if (request === this.request && this.state === 'running') this.loop?.start();
      }).catch(() => {
        if (request === this.request && this.state === 'running') {
          this.fail('Kamera tidak dapat dilanjutkan. Silakan mulai lagi.');
        }
      });
    }
  };

  private readonly onPageHide = (): void => {
    this.fail('Sesi dihentikan. Silakan mulai kembali.');
  };

  private fail(message: string): void {
    this.stop();
    this.callbacks.error(message);
  }

  stop(): void {
    this.request?.abort();
    this.request = undefined;
    this.loop?.stop();
    this.loop = undefined;
    this.vision?.destroy();
    this.vision = undefined;
    this.camera.stop();
    this.callbacks.pause();
    this.state = 'idle';
  }

  destroy(): void {
    this.stop();
    this.state = 'disposed';
    document.removeEventListener('visibilitychange', this.onVisibilityChange);
    window.removeEventListener('pagehide', this.onPageHide);
  }
}
