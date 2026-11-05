import type { NormalizedLandmark } from '@mediapipe/tasks-vision';

type Slot = 'left' | 'right';

// MediaPipe hand topology (21 landmarks). Kept local so the main bundle does not
// pull in @mediapipe/tasks-vision just for this constant.
const CONNECTIONS: ReadonlyArray<readonly [number, number]> = [
  [0, 1], [1, 2], [2, 3], [3, 4],
  [0, 5], [5, 6], [6, 7], [7, 8],
  [5, 9], [9, 10], [10, 11], [11, 12],
  [9, 13], [13, 14], [14, 15], [15, 16],
  [13, 17], [0, 17], [17, 18], [18, 19], [19, 20],
];
const CONTROL_TIPS = new Set([8, 12]); // index + middle fingertips drive the wayang arms
const COLORS: Record<Slot, string> = { left: '#f2c46b', right: '#fff4d9' };

/** Draws tracked hand landmarks over the mirrored camera preview. Redraws only when a result arrives. */
export class HandOverlay {
  private readonly canvas = document.createElement('canvas');
  private readonly context = this.canvas.getContext('2d');

  constructor(private readonly video: HTMLVideoElement) {
    this.canvas.id = 'hand-overlay';
    this.canvas.hidden = true;
    this.canvas.setAttribute('aria-hidden', 'true');
    video.after(this.canvas);
  }

  draw(hands: Partial<Record<Slot, NormalizedLandmark[] | undefined>>): void {
    const ctx = this.context;
    if (!ctx || this.video.hidden || !this.video.videoWidth) { this.clear(); return; }
    this.canvas.hidden = false;
    const width = this.canvas.clientWidth;
    const height = this.canvas.clientHeight;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (this.canvas.width !== Math.round(width * dpr) || this.canvas.height !== Math.round(height * dpr)) {
      this.canvas.width = Math.round(width * dpr);
      this.canvas.height = Math.round(height * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);

    // Match the preview's object-fit: cover crop; CSS mirrors the canvas like the video.
    const scale = Math.max(width / this.video.videoWidth, height / this.video.videoHeight);
    const drawnWidth = this.video.videoWidth * scale;
    const drawnHeight = this.video.videoHeight * scale;
    const offsetX = (width - drawnWidth) / 2;
    const offsetY = (height - drawnHeight) / 2;
    const point = (landmark: NormalizedLandmark): [number, number] =>
      [offsetX + landmark.x * drawnWidth, offsetY + landmark.y * drawnHeight];

    for (const slot of ['left', 'right'] as const) {
      const landmarks = hands[slot];
      if (!landmarks || landmarks.length < 21) continue;
      ctx.strokeStyle = COLORS[slot];
      ctx.fillStyle = COLORS[slot];
      ctx.lineWidth = 1.5;
      ctx.globalAlpha = 0.85;
      ctx.beginPath();
      for (const [a, b] of CONNECTIONS) {
        ctx.moveTo(...point(landmarks[a]));
        ctx.lineTo(...point(landmarks[b]));
      }
      ctx.stroke();
      ctx.globalAlpha = 1;
      landmarks.forEach((landmark, index) => {
        const [x, y] = point(landmark);
        ctx.beginPath();
        ctx.arc(x, y, CONTROL_TIPS.has(index) ? 3.6 : 1.9, 0, Math.PI * 2);
        ctx.fill();
        if (CONTROL_TIPS.has(index)) {
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.arc(x, y, 6, 0, Math.PI * 2);
          ctx.stroke();
        }
      });
    }
  }

  clear(): void {
    this.context?.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.canvas.hidden = true;
  }

  destroy(): void { this.canvas.remove(); }
}
