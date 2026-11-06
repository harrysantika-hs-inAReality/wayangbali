import { arm, character } from './definition';

// Tune shoulder, elbow and hand anchor centers here; preserve full-canvas alignment.
export const wayang04 = character('wayang04', 'Delem (atau Melem)', 1.1, [
  arm('wayang04', 'left', { x: 589, y: 614 }, { x: 392, y: 642 }, { x: 230, y: 629 }, 'index',
    { elbowDirection: 1, gainX: 3.8, gainY: 3.8, smoothFactor: 0.26 }),
  arm('wayang04', 'right', { x: 599, y: 609 }, { x: 724, y: 610 }, { x: 755, y: 777 }, 'middle',
    { elbowDirection: 1, gainX: 2.4, gainY: 2.4, smoothFactor: 0.22 }),
], true, 0.18);
