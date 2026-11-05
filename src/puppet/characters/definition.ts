import type { PuppetArmDefinition, PuppetDefinition, PuppetPoint } from '../PuppetDefinition';

export const assetPath = (id: string): string => `${import.meta.env.BASE_URL}assets/characters/${id}/`;

export interface ArmTuning {
  elbowDirection: 1 | -1;
  gainX: number;
  gainY: number;
  smoothFactor: number;
  singleAssetNames?: boolean;
}

/** Pivots are estimated in the existing logical 1024 x 1365 canvas. */
export function arm(character: string, id: string, shoulder: PuppetPoint, elbow: PuppetPoint,
  hand: PuppetPoint, finger: 'index' | 'middle', tuning: ArmTuning): PuppetArmDefinition {
  const path = assetPath(character);
  const prefix = tuning.singleAssetNames ? '' : `${id}_`;
  return {
    id, upperArmAsset: `${path}${prefix}upper_arm.png`,
    forearmHandAsset: `${path}${prefix}forearm_hand.png`,
    shoulderPivot: shoulder, elbowPivot: elbow, handAnchor: hand,
    shoulderMinRotation: -0.8, shoulderMaxRotation: 0.8,
    elbowMinRotation: -1.2, elbowMaxRotation: 1.2,
    elbowDirection: tuning.elbowDirection, finger,
    gainX: tuning.gainX, gainY: tuning.gainY,
    smoothFactor: tuning.smoothFactor,
  };
}

export function character(id: string, name: string, defaultScale: number, arms: PuppetArmDefinition[],
  reference: boolean, bodySmoothing: number, artworkFacing: 'left' | 'right' = 'left'): PuppetDefinition {
  const path = assetPath(id);
  return {
    id, name, artworkFacing, canvas: { width: 1024, height: 1365 },
    defaultScale, rootPivot: { x: 512, y: 1000 },
    assets: { body: `${path}body.png`, mainRod: `${path}main_rod.png`,
      ...(reference ? { reference: `${path}reference.png` } : {}) },
    arms, layers: ['mainRod', ...arms.filter(a => a.finger === 'middle').map(a => a.id),
      'body', ...arms.filter(a => a.finger === 'index').map(a => a.id)],
    movementBounds: { minX: 0.05, maxX: 0.95, minY: 0.35, maxY: 0.85 },
    smoothing: bodySmoothing, bodyRotation: { gain: 0.2, max: Math.PI / 12 },
  };
}
