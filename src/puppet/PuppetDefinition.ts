export interface PuppetPoint { x: number; y: number }
export interface RotationLimit { min: number; max: number }
export interface MovementBounds { minX: number; maxX: number; minY: number; maxY: number }

export interface PuppetArmDefinition {
  id: string;
  upperArmAsset: string;
  forearmHandAsset: string;
  shoulderPivot: PuppetPoint;
  elbowPivot: PuppetPoint;
  handAnchor: PuppetPoint;
  shoulderMinRotation: number;
  shoulderMaxRotation: number;
  elbowMinRotation: number;
  elbowMaxRotation: number;
  elbowDirection: 1 | -1;
  finger: 'index' | 'middle';
  gainX: number;
  gainY: number;
  smoothFactor: number;
}

export interface PuppetDefinition {
  id: string;
  name: string;
  artworkFacing: 'left' | 'right';
  /** Shared logical full-canvas coordinates; uniformly scaled artwork. */
  canvas: { width: number; height: number };
  defaultScale: number;
  assets: { body: string; mainRod?: string; reference?: string };
  rootPivot: PuppetPoint;
  arms: readonly PuppetArmDefinition[];
  /** Back to front: body, optional mainRod, and arm IDs. */
  layers: readonly string[];
  movementBounds: MovementBounds;
  smoothing: number;
  bodyRotation: { gain: number; max: number };
}
