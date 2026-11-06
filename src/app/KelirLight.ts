// Home page: the pointer is the blencong lamp. Each puppet's shadow on the kelir
// is pushed away from the light, and the kelir glow follows it.
// Work only happens on pointer events (one rAF per frame), never in an idle loop.

const STRENGTH = 0.14;   // shadow offset per px of puppet-to-light distance
const MAX_X = 70;        // px
const MAX_Y = 34;        // px
const clamp = (v: number, max: number): number => Math.max(-max, Math.min(max, v));

export function attachKelirLight(host: HTMLElement): () => void {
  const kelir = host.querySelector<HTMLElement>('.kelir');
  if (!kelir) return () => undefined;
  const figures = [...kelir.querySelectorAll<HTMLElement>('.kelir-wayang')];
  const shadows = figures.map(figure => figure.querySelector<HTMLElement>('.kelir-shadow'));
  let pointer: { x: number; y: number } | undefined;
  let frame = 0;

  const update = (): void => {
    frame = 0;
    const box = kelir.getBoundingClientRect();
    if (pointer) {
      kelir.style.setProperty('--lamp-x', `${((pointer.x - box.left) / box.width) * 100}%`);
      kelir.style.setProperty('--lamp-y', `${((pointer.y - box.top) / box.height) * 100}%`);
    } else {
      kelir.style.removeProperty('--lamp-x');
      kelir.style.removeProperty('--lamp-y');
    }
    // Default light = the lamp position defined in CSS for this breakpoint.
    const style = getComputedStyle(kelir);
    const lightX = pointer?.x ?? box.left + (parseFloat(style.getPropertyValue('--lamp-x')) / 100) * box.width;
    const lightY = pointer?.y ?? box.top + (parseFloat(style.getPropertyValue('--lamp-y')) / 100) * box.height;
    figures.forEach((figure, index) => {
      const shadow = shadows[index];
      if (!shadow) return;
      const rect = figure.getBoundingClientRect();
      const dx = rect.left + rect.width / 2 - lightX;
      const dy = rect.top + rect.height * 0.55 - lightY;
      shadow.style.translate = `${clamp(dx * STRENGTH, MAX_X).toFixed(1)}px ${clamp(dy * STRENGTH * 0.6, MAX_Y).toFixed(1)}px`;
    });
  };

  const schedule = (): void => { if (!frame) frame = requestAnimationFrame(update); };
  const onMove = (event: PointerEvent): void => { pointer = { x: event.clientX, y: event.clientY }; schedule(); };
  const onLeave = (event: PointerEvent): void => { if (event.pointerType === 'mouse') { pointer = undefined; schedule(); } };

  host.addEventListener('pointermove', onMove, { passive: true });
  host.addEventListener('pointerdown', onMove, { passive: true });
  host.addEventListener('pointerleave', onLeave);
  window.addEventListener('resize', schedule);
  schedule();

  return () => {
    cancelAnimationFrame(frame);
    host.removeEventListener('pointermove', onMove);
    host.removeEventListener('pointerdown', onMove);
    host.removeEventListener('pointerleave', onLeave);
    window.removeEventListener('resize', schedule);
  };
}
