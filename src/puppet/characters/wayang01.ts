import { arm, character } from './definition';

// Tune shoulder, elbow and hand anchor centers here; preserve full-canvas alignment.
export const wayang01 = character('wayang01', 'Twalen (atau Malen)', 1, [
  arm('wayang01', 'left', { x: 600, y: 627 }, { x: 412, y: 697 }, { x: 219, y: 684 }, 'index',
    { elbowDirection: 1, gainX: 4, gainY: 4, smoothFactor: 0.28 }),
  arm('wayang01', 'right', { x: 600, y: 627 }, { x: 793, y: 650 }, { x: 798, y: 824 }, 'middle',
    { elbowDirection: 1, gainX: 2.5, gainY: 2.5, smoothFactor: 0.24 }),
], true, 0.20);
