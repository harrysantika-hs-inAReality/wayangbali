interface Point { x: number; y: number }

export const facingGestureSettings = {
  holdMs: 900,
  releaseMs: 450,
  cooldownMs: 1800,
  maxFrameGapMs: 250,
};

/** One deliberate four-finger hold per release; missing tracking never rearms it. */
export class FacingGesture {
  private armed = false;
  private heldSince?: number;
  private releasedSince?: number;
  private lastTimestamp = -Infinity;
  private lastFlip = -Infinity;

  interrupt(): void {
    this.armed = false;
    this.heldSince = undefined;
    this.releasedSince = undefined;
  }

  update(landmarks: readonly Point[] | undefined, timestamp: number, aspectRatio: number): boolean {
    if (!Number.isFinite(timestamp) || timestamp <= this.lastTimestamp) return false;
    if (timestamp - this.lastTimestamp > facingGestureSettings.maxFrameGapMs) this.interrupt();
    this.lastTimestamp = timestamp;
    if (!landmarks || landmarks.length < 21 || !Number.isFinite(aspectRatio) || aspectRatio <= 0
      || landmarks.some(point => !Number.isFinite(point.x) || !Number.isFinite(point.y))) {
      this.interrupt();
      return false;
    }
    // Pixel-proportional distances work with either hand, rotation and camera mirroring.
    const distance = (a: number, b: number): number => Math.hypot(
      landmarks[a].x - landmarks[b].x, (landmarks[a].y - landmarks[b].y) * aspectRatio);
    const palm = distance(0, 9);
    if (palm < 0.025) { this.interrupt(); return false; }
    let extended = 0;
    let curled = 0;
    for (const base of [5, 9, 13, 17]) {
      const length = distance(base, base + 1) + distance(base + 1, base + 2) + distance(base + 2, base + 3);
      const straightness = length > 0 ? distance(base, base + 3) / length : 0;
      const tipReach = distance(0, base + 3);
      const knuckleReach = distance(0, base + 1);
      if (straightness > 0.9 && tipReach > knuckleReach * 1.15) extended++;
      if (straightness < 0.7 || tipReach < knuckleReach * 1.02) curled++;
    }
    // Fold the thumb across the palm to distinguish this from an ordinary open hand.
    const thumbReach = distance(4, 9) / palm;
    const active = extended === 4 && thumbReach < 0.65;
    const released = curled >= 2 || thumbReach > 0.95;
    if (!this.armed) {
      if (!released) this.releasedSince = undefined;
      else {
        this.releasedSince ??= timestamp;
        if (timestamp - this.releasedSince >= facingGestureSettings.releaseMs) this.armed = true;
      }
      return false;
    }
    if (!active || timestamp - this.lastFlip < facingGestureSettings.cooldownMs) {
      this.heldSince = undefined;
      return false;
    }
    this.heldSince ??= timestamp;
    if (timestamp - this.heldSince < facingGestureSettings.holdMs) return false;
    this.lastFlip = timestamp;
    this.interrupt();
    return true;
  }
}
