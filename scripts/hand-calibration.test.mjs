import assert from 'node:assert/strict';
import test from 'node:test';
import { HandCalibration } from '../src/app/HandCalibration.ts';

test('normal detection requires 1.5 seconds of presence', () => {
  const calibration = new HandCalibration();
  for (let time = 0; time < 1500; time += 50) assert.equal(calibration.update(true, time), false);
  assert.equal(calibration.update(true, 1500), true);
});

test('slow detection can complete calibration without an endless reset', () => {
  const calibration = new HandCalibration();
  for (let time = 0; time < 2500; time += 500) assert.equal(calibration.update(true, time), false);
  assert.equal(calibration.update(true, 2500), true);
});

test('one long gap cannot complete calibration', () => {
  const calibration = new HandCalibration();
  assert.equal(calibration.update(true, 0), false);
  assert.equal(calibration.update(true, 10000), false);
});

test('missing selected hands and session pauses reset accumulated presence', () => {
  const calibration = new HandCalibration();
  for (let time = 0; time <= 1200; time += 300) calibration.update(true, time);
  assert.equal(calibration.update(false, 1500), false);
  assert.equal(calibration.update(true, 1800), false);
  for (let time = 2100; time <= 3000; time += 300) calibration.update(true, time);
  calibration.reset();
  assert.equal(calibration.update(true, 10000), false);
  assert.equal(calibration.update(true, 10300), false);
});
