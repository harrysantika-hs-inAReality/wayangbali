import { arm, character } from './definition';

// Tune shoulder, elbow and hand anchor centers here; preserve full-canvas alignment.
export const wayang02 = character('wayang02', 'Merdah', 0.83, [
  arm('wayang02', 'left', { x: 470, y: 565 }, { x: 640, y: 721 }, { x: 845, y: 713 }, 'index',
    { elbowDirection: -1, gainX: 4, gainY: 4, smoothFactor: 0.26, singleAssetNames: true }),
], true, 0.18, 'right');
