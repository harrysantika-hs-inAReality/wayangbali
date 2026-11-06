import type { PuppetPoint, RotationLimit } from './PuppetDefinition';

export interface ArmRotations {
  shoulder: number;
  elbow: number;
}

export function shortestAngle(angle: number): number {
  return Math.atan2(Math.sin(angle), Math.cos(angle));
}

const clamp = (value: number, min: number, max: number): number => Math.min(max, Math.max(min, value));

/** Solves in logical artwork coordinates; outputs rotations relative to the PNG pose. */
export class TwoBoneIK {
  readonly upperLength: number;
  readonly lowerLength: number;
  readonly maxReach: number;
  private readonly upperRestAngle: number;
  private readonly elbowRestAngle: number;
  private readonly restTargetAngle: number;

  constructor(
    private readonly shoulder: PuppetPoint,
    elbow: PuppetPoint,
    handAnchor: PuppetPoint,
    private readonly elbowDirection: 1 | -1,
    private readonly shoulderLimit: RotationLimit,
    private readonly elbowLimit: RotationLimit,
  ) {
    const upperX = elbow.x - shoulder.x;
    const upperY = elbow.y - shoulder.y;
    const lowerX = handAnchor.x - elbow.x;
    const lowerY = handAnchor.y - elbow.y;
    this.upperLength = Math.hypot(upperX, upperY);
    this.lowerLength = Math.hypot(lowerX, lowerY);
    this.maxReach = this.upperLength + this.lowerLength;
    this.upperRestAngle = Math.atan2(upperY, upperX);
    this.elbowRestAngle = shortestAngle(Math.atan2(lowerY, lowerX) - this.upperRestAngle);
    this.restTargetAngle = Math.atan2(handAnchor.y - shoulder.y, handAnchor.x - shoulder.x);
  }

  /** Reuses output; an invalid target or zero-length bone keeps the previous solution. */
  solve(target: PuppetPoint, output: ArmRotations): boolean {
    const dx = target.x - this.shoulder.x;
    const dy = target.y - this.shoulder.y;
    const distance = Math.hypot(dx, dy);
    if (!Number.isFinite(distance) || !Number.isFinite(this.maxReach)
      || this.upperLength < 1e-6 || this.lowerLength < 1e-6) return false;

    // Clamp to the reachable annulus; stay just inside straight/folded
    // singularities so the configured bend direction remains well-defined.
    const epsilon = Math.min(this.upperLength, this.lowerLength) * 1e-6;
    const reach = clamp(distance, Math.abs(this.upperLength - this.lowerLength) + epsilon, this.maxReach - epsilon);
    const direction = distance > epsilon ? Math.atan2(dy, dx) : this.restTargetAngle;
    const cosine = clamp(
      (reach * reach - this.upperLength ** 2 - this.lowerLength ** 2)
        / (2 * this.upperLength * this.lowerLength),
      -1, 1,
    );
    const bend = this.elbowDirection * Math.acos(cosine);
    const upperAngle = direction - Math.atan2(
      this.lowerLength * Math.sin(bend),
      this.upperLength + this.lowerLength * Math.cos(bend),
    );
    // Choose the equivalent shoulder angle nearest the previous solution,
    // avoiding a ±π branch jump when a target passes across the angle seam.
    const shoulderRotation = output.shoulder + shortestAngle(upperAngle - this.upperRestAngle - output.shoulder);
    // Do not wrap the elbow: the fixed bend branch must not invert at ±π.
    const elbowRotation = bend - this.elbowRestAngle;
    output.shoulder = clamp(shoulderRotation, this.shoulderLimit.min, this.shoulderLimit.max);
    output.elbow = clamp(elbowRotation, this.elbowLimit.min, this.elbowLimit.max);
    return true;
  }
}
