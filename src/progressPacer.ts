/**
 * Smooths a loading percentage for display: the shown value chases the real
 * progress but can rise at most 100% per `minMs`, so a loading screen always
 * runs visibly from 0% to 100% and never finishes before `minMs`.
 */
export interface ProgressPacer {
  /** Report real progress (0..100). Values never go backwards. */
  set(percent: number): void;
  /** Mark loading complete; resolves once the display has reached 100%. */
  finish(): Promise<void>;
  cancel(): void;
}

export function createProgressPacer(render: (percent: number) => void, minMs = 2000): ProgressPacer {
  const start = performance.now();
  let target = 0;
  let shown = 0;
  let timer = 0;
  let cancelled = false;
  let resolveDone: (() => void) | undefined;

  // A 30 fps timer (PRD cap); unlike requestAnimationFrame it keeps running in background tabs.
  const tick = (): void => {
    timer = 0;
    if (cancelled) return;
    const now = performance.now();
    const goal = Math.min(target, ((now - start) / minMs) * 100);
    shown = goal - shown < 0.5 ? goal : shown + (goal - shown) * 0.2;
    render(shown);
    if (shown >= 100) { resolveDone?.(); return; }
    if (shown >= target) return; // idle until set()/finish() raises the target
    timer = window.setTimeout(tick, 33);
  };
  const run = (): void => { if (!timer && !cancelled && shown < 100) timer = window.setTimeout(tick, 33); };

  render(0);
  return {
    set(percent) { target = Math.max(target, Math.min(100, percent)); run(); },
    finish() {
      target = 100;
      return new Promise(resolve => {
        if (shown >= 100) { resolve(); return; }
        resolveDone = resolve;
        run();
      });
    },
    cancel() { cancelled = true; window.clearTimeout(timer); },
  };
}
