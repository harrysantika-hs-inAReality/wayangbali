import type { PuppetRig } from '../puppet/PuppetRig';
import type { PuppetArmDefinition, PuppetPoint, MovementBounds } from '../puppet/PuppetDefinition';
import { shortestAngle, TwoBoneIK } from '../puppet/TwoBoneIK';
import type { ArmRotations } from '../puppet/TwoBoneIK';
import type { PixiRenderer } from '../rendering/PixiRenderer';
import { FacingGesture } from './FacingGesture';

interface HandPoint { x: number; y: number }
const palmIndices = [0, 5, 9, 13, 17] as const;

interface ArmState {
  definition: PuppetArmDefinition;
  solver: TwoBoneIK;
  anchor: PuppetPoint;
  target: PuppetPoint;
  angles: ArmRotations;
  current: ArmRotations;
  tracked: boolean;
}

export const handControlSettings = {
  trackingLossGraceMs: 300,
};

const clamp = (value: number, min: number, max: number): number => Math.min(max, Math.max(min, value));

export class HandPuppetController {
  private readonly target = { x: 0.5, y: 0.5, rotation: 0 };
  private readonly current = { x: 0.5, y: 0.5, rotation: 0 };
  private readonly localPosition = { x: 0, y: 0 };
  private lastSeen = -Infinity;
  private lastResultTimestamp = -Infinity;
  private following = false;
  private readonly arms: ArmState[];
  private readonly facingGesture = new FacingGesture();

  constructor(
    private readonly puppet: PuppetRig,
    private readonly renderer: PixiRenderer,
    private readonly video: HTMLVideoElement,
    private readonly bounds: MovementBounds = puppet.definition.movementBounds,
    private readonly settings = handControlSettings,
  ) {
    this.arms = puppet.definition.arms.map(arm => this.createArm(arm));
  }

  acceptLandmarks(landmarks: readonly HandPoint[] | undefined, timestamp: number): void {
    if (timestamp <= this.lastResultTimestamp) return;
    this.lastResultTimestamp = timestamp;
    if (this.facingGesture.update(landmarks, timestamp, this.video.videoHeight / this.video.videoWidth)) {
      this.puppet.flipFacing();
    }
    // A missing result keeps the last valid targets through the existing grace
    // period. The visual loop continues interpolation without snapping/resetting.
    if (!landmarks || landmarks.length < 21) return;
    let x = 0;
    let y = 0;
    // Average wrist and the four finger bases; ignore fingertip movement.
    for (const index of palmIndices) {
      x += landmarks[index].x;
      y += landmarks[index].y;
    }
    this.target.x = 1 - x / 5; // Match the CSS-mirrored preview.
    this.target.y = y / 5;
    const wrist = landmarks[0];
    const middle = landmarks[9];
    const angle = Math.atan2(
      -(middle.x - wrist.x) * this.video.videoWidth,
      (wrist.y - middle.y) * this.video.videoHeight,
    );
    this.target.rotation = clamp(angle * this.puppet.definition.bodyRotation.gain, -this.puppet.definition.bodyRotation.max, this.puppet.definition.bodyRotation.max);
    this.lastSeen = timestamp;
    for (const arm of this.arms) {
      this.setArmTarget(arm, landmarks[arm.definition.finger === 'index' ? 8 : 12], x / 5, y / 5);
    }

    if (!this.following) {
      const origin = this.renderer.getPuppetStagePosition(this.puppet);
      this.current.x = origin.x / this.renderer.screen.width;
      this.current.y = origin.y / this.renderer.screen.height;
      this.current.rotation = this.puppet.root.rotation;
      this.following = true;
    }
  }

  update(deltaMS: number, timestamp: number): void {
    if (!this.following) return;
    const { width, height } = this.renderer.screen;
    const trackingActive = timestamp - this.lastSeen <= this.settings.trackingLossGraceMs;
    if (trackingActive) {
      // Match centered object-fit: cover, including the video cropped offscreen.
      const cover = Math.max(width / this.video.videoWidth, height / this.video.videoHeight);
      const videoWidth = this.video.videoWidth * cover;
      const videoHeight = this.video.videoHeight * cover;
      const x = clamp(((width - videoWidth) / 2 + this.target.x * videoWidth) / width, this.bounds.minX, this.bounds.maxX);
      const y = clamp(((height - videoHeight) / 2 + this.target.y * videoHeight) / height, this.bounds.minY, this.bounds.maxY);
      const alpha = 1 - Math.pow(1 - clamp(this.puppet.definition.smoothing, 0, 1), Math.min(deltaMS, 100) / (1000 / 30));
      this.current.x += (x - this.current.x) * alpha;
      this.current.y += (y - this.current.y) * alpha;
      this.current.rotation += (this.target.rotation - this.current.rotation) * alpha;
    }
    // After the grace period, hold the actual last pose until detection returns.
    // Convert stage pixels into the existing rig parent's coordinates.
    this.renderer.stageToPuppetPosition(this.current.x * width, this.current.y * height, this.localPosition);
    this.puppet.setPosition(this.localPosition.x, this.localPosition.y);
    this.puppet.setBodyRotation(this.current.rotation);
    if (trackingActive) {
      this.updateArms(deltaMS);
    }
  }

  private createArm(definition: PuppetArmDefinition): ArmState {
    const anchor = definition.handAnchor;
    const current = { shoulder: 0, elbow: 0 };
    return {
      definition,
      solver: new TwoBoneIK(definition.shoulderPivot, definition.elbowPivot, anchor,
        definition.elbowDirection,
        { min: definition.shoulderMinRotation, max: definition.shoulderMaxRotation },
        { min: definition.elbowMinRotation, max: definition.elbowMaxRotation }),
      anchor, target: { ...anchor }, angles: { ...current }, current, tracked: false,
    };
  }

  private setArmTarget(arm: ArmState, tip: HandPoint, palmX: number, palmY: number): void {
    const { gainX, gainY } = arm.definition;
    if (!this.video.videoWidth || !this.video.videoHeight) return;
    // Use palm-relative vectors only. Mirror X once, and correct the camera
    // aspect ratio so both axes use camera-width units. Map into local artwork
    // space around the hand anchor, independently of body position/viewport size.
    const relativeX = -(tip.x - palmX) * this.puppet.horizontalDirection;
    const relativeY = (tip.y - palmY) * this.video.videoHeight / this.video.videoWidth;
    arm.target.x = arm.anchor.x + relativeX * arm.solver.maxReach * gainX;
    arm.target.y = arm.anchor.y + relativeY * arm.solver.maxReach * gainY;
    arm.tracked = arm.solver.solve(arm.target, arm.angles);
  }

  private updateArms(deltaMS: number): void {
    for (const arm of this.arms) {
      if (!arm.tracked) continue;
      const factor = clamp(arm.definition.smoothFactor, 0, 1);
      const alpha = 1 - Math.pow(1 - factor, Math.min(deltaMS, 100) / (1000 / 30));
      arm.current.shoulder = clamp(
        arm.current.shoulder + shortestAngle(arm.angles.shoulder - arm.current.shoulder) * alpha,
        arm.definition.shoulderMinRotation, arm.definition.shoulderMaxRotation,
      );
      arm.current.elbow = clamp(
        arm.current.elbow + shortestAngle(arm.angles.elbow - arm.current.elbow) * alpha,
        arm.definition.elbowMinRotation, arm.definition.elbowMaxRotation,
      );
      this.puppet.setArmRotation(arm.definition.id, arm.current.shoulder, arm.current.elbow);
    }
  }

  stop(): void {
    this.facingGesture.interrupt();
    this.lastSeen = -Infinity;
    for (const arm of this.arms) arm.tracked = false;
  }
}
