import assert from 'node:assert/strict';
import test from 'node:test';
import { FacingGesture } from '../src/controller/FacingGesture.ts';

function hand(open = true, thumbFolded = true, angle = 0, mirror = 1) {
  const points = Array.from({ length: 21 }, () => ({ x: 0, y: 0 }));
  for (const [i, base] of [5, 9, 13, 17].entries()) {
    const x = (i - 1.5) * 0.05;
    for (let joint = 0; joint < 4; joint++) {
      points[base + joint] = { x, y: open ? -0.15 - joint * 0.06 : [-0.15, -0.21, -0.14, -0.09][joint] };
    }
  }
  points[4] = thumbFolded ? { x: -0.01, y: -0.12 } : { x: -0.25, y: -0.12 };
  return points.map(({ x, y }) => ({
    x: 0.5 + mirror * (x * Math.cos(angle) - y * Math.sin(angle)),
    y: 0.5 + (x * Math.sin(angle) + y * Math.cos(angle)) / 0.75,
  }));
}

function stream() {
  const detector = new FacingGesture();
  let timestamp = 0;
  let flips = 0;
  return {
    detector,
    get flips() { return flips; },
    feed(points, duration) {
      for (let elapsed = 0; elapsed < duration; elapsed += 50) {
        timestamp += 50;
        if (detector.update(points, timestamp, 0.75)) flips++;
      }
    },
    gap(duration) { timestamp += duration; },
  };
}

test('requires release first, sustained hold, and another release before repeating', () => {
  const s = stream();
  s.feed(hand(), 2000);
  assert.equal(s.flips, 0, 'startup pose must not flip');
  s.feed(hand(false), 600);
  s.feed(hand(), 800);
  assert.equal(s.flips, 0, 'short hold must not flip');
  s.feed(hand(), 200);
  assert.equal(s.flips, 1);
  s.feed(hand(), 5000);
  assert.equal(s.flips, 1, 'holding must never repeat');
  s.feed(hand(false), 600);
  s.feed(hand(), 1000);
  assert.equal(s.flips, 2);
});

test('noise, open five-finger palm, and short release cannot trigger repeated flips', () => {
  const s = stream();
  s.feed(hand(true, false), 2000);
  assert.equal(s.flips, 0);
  for (let i = 0; i < 8; i++) {
    s.feed(hand(), 300);
    s.feed(hand(false), 100);
  }
  assert.equal(s.flips, 0);
  s.feed(hand(), 1000);
  assert.equal(s.flips, 1);
  s.feed(hand(false), 200);
  s.feed(hand(), 3000);
  assert.equal(s.flips, 1);
});

test('tracking loss, pauses and frame gaps require deliberate rearming', () => {
  for (const interrupt of [s => s.feed(undefined, 50), s => s.gap(1000), s => s.detector.interrupt()]) {
    const s = stream();
    s.feed(hand(false), 600);
    s.feed(hand(), 700);
    interrupt(s);
    s.feed(hand(), 2000);
    assert.equal(s.flips, 0);
    s.feed(hand(false), 600);
    s.feed(hand(), 1000);
    assert.equal(s.flips, 1);
    s.feed(undefined, 500);
    s.feed(hand(), 3000);
    assert.equal(s.flips, 1);
  }
});

test('cooldown applies even after a valid release', () => {
  const s = stream();
  s.feed(hand(false), 600);
  s.feed(hand(), 1000);
  s.feed(hand(false), 600);
  s.feed(hand(), 1000);
  assert.equal(s.flips, 1);
  s.feed(hand(), 1300);
  assert.equal(s.flips, 2);
});

test('both hands and rotated poses work independently', () => {
  for (const mirror of [-1, 1]) for (const angle of [0, Math.PI / 3, -Math.PI / 2]) {
    const s = stream();
    s.feed(hand(false, true, angle, mirror), 600);
    s.feed(hand(true, true, angle, mirror), 1000);
    assert.equal(s.flips, 1);
  }
  const left = stream();
  const right = stream();
  left.feed(hand(false), 600);
  right.feed(hand(false), 600);
  left.feed(hand(), 1000);
  right.feed(hand(true, false), 1000);
  assert.equal(left.flips, 1);
  assert.equal(right.flips, 0);
});
