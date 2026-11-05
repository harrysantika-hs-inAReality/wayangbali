import type { HandLandmarkerResult, NormalizedLandmark } from '@mediapipe/tasks-vision';
import { shortestAngle } from '../puppet/TwoBoneIK';

export type HandSlot = 'left' | 'right';
export const handSlots = ['left', 'right'] as const;
interface Detection {
  landmarks: NormalizedLandmark[];
  x: number; y: number; angle: number;
  side?: HandSlot; confidence: number;
}
interface Track { x: number; y: number; vx: number; vy: number; angle: number; lastSeen: number }

/** Tracks are permanently named for physical hands, including the unused slot. */
export class HandTrackManager {
  private tracks: Partial<Record<HandSlot, Track>> = {};

  update(result: HandLandmarkerResult, timestamp: number): Partial<Record<HandSlot, NormalizedLandmark[]>> {
    const detections: Detection[] = result.landmarks.slice(0, 2).map((landmarks, i) => {
      let x = 0, y = 0;
      for (const index of [0, 5, 9, 13, 17]) { x += landmarks[index].x / 5; y += landmarks[index].y / 5; }
      const category = result.handedness[i]?.[0];
      // The installed Hand Landmarker reports physical handedness for this raw
      // video input. CSS mirroring affects only the preview, never ownership.
      const side = category?.categoryName === 'Left' ? 'left'
        : category?.categoryName === 'Right' ? 'right' : undefined;
      return { landmarks, x, y, side, confidence: category?.score ?? 0,
        angle: Math.atan2(landmarks[9].y - landmarks[0].y, landmarks[9].x - landmarks[0].x) };
    });
    const choices = [-1, ...detections.map((_, i) => i)];
    let best = Infinity;
    let assignment = [-1, -1];
    // Include unmatched choices; a disappearing hand must not force reassignment.
    for (const left of choices) for (const right of choices) {
      if (left >= 0 && left === right) continue;
      const cost = (left < 0 ? 0.85 : this.cost('left', detections[left], timestamp))
        + (right < 0 ? 0.85 : this.cost('right', detections[right], timestamp));
      if (cost < best) { best = cost; assignment = [left, right]; }
    }
    const output: Partial<Record<HandSlot, NormalizedLandmark[]>> = {};
    handSlots.forEach((slot, i) => {
      const detection = detections[assignment[i]];
      if (!detection) return;
      const previous = this.tracks[slot];
      const dt = previous ? timestamp - previous.lastSeen : Infinity;
      const continuous = previous && dt > 0 && dt < 300;
      this.tracks[slot] = { x: detection.x, y: detection.y, angle: detection.angle, lastSeen: timestamp,
        vx: continuous ? previous.vx * 0.5 + (detection.x - previous.x) / dt * 0.5 : 0,
        vy: continuous ? previous.vy * 0.5 + (detection.y - previous.y) / dt * 0.5 : 0 };
      output[slot] = detection.landmarks;
    });
    return output;
  }

  private cost(slot: HandSlot, detection: Detection, timestamp: number): number {
    const track = this.tracks[slot];
    const age = track ? timestamp - track.lastSeen : Infinity;
    if (!track || age > 800) {
      // Landmark detection has already passed MediaPipe's presence threshold.
      // Do not discard a valid first track only because mobile-camera
      // handedness confidence is below an additional arbitrary threshold.
      if (detection.side === slot) return 0.2 + (1 - detection.confidence) * 0.2;
      if (detection.side) return Infinity;
      // Rare runtimes omit handedness. Raw front-camera coordinates put the
      // physical left hand on image-right and physical right on image-left.
      const expectedImageRight = slot === 'left';
      return (detection.x >= 0.5) === expectedImageRight ? 0.55 : 0.95;
    }
    const prediction = Math.min(age, 150);
    const distance = Math.hypot(detection.x - track.x - track.vx * prediction,
      detection.y - track.y - track.vy * prediction);
    if (distance > 0.35) return Infinity;
    const handedness = detection.side && detection.side !== slot ? 0.4 * detection.confidence : 0;
    const orientation = Math.abs(shortestAngle(detection.angle - track.angle)) / Math.PI;
    return distance * 2.5 + orientation * 0.12 + handedness;
  }

  reset(): void { this.tracks = {}; }
}
