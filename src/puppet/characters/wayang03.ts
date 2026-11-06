import { arm, character } from './definition';

// Tune shoulder, elbow and hand anchor centers here; preserve full-canvas alignment.
export const wayang03 = character('wayang03', 'Sangut', 1.05, [
  arm('wayang03', 'left', { x: 360, y: 615 }, { x: 271, y: 781 }, { x: 120, y: 802 }, 'index',
    { elbowDirection: 1, gainX: 4, gainY: 4, smoothFactor: 0.28 }),
  arm('wayang03', 'right', { x: 565, y: 637 }, { x: 773, y: 675 }, { x: 760, y: 814 }, 'middle',
    { elbowDirection: 1, gainX: 2.5, gainY: 2.5, smoothFactor: 0.24 }),
], true, 0.22);
