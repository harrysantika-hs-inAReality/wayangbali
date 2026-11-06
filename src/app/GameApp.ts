import { Tutor, tutorIcon } from '../tutor/Tutor';
import { attachKelirLight } from './KelirLight';
import type { HandLandmarkerResult } from '@mediapipe/tasks-vision';
import backsoundUrl from '../../assett/backsound.mp3';
import { CameraSession } from './CameraSession';
import { HandCalibration } from './HandCalibration';
import { HandOverlay } from '../camera/HandOverlay';
import { createProgressPacer } from '../progressPacer';
import type { ProgressPacer } from '../progressPacer';
import { HandPuppetController } from '../controller/HandPuppetController';
import { PuppetRig } from '../puppet/PuppetRig';
import { characterCatalog } from '../puppet/characters/catalog';
import { PixiRenderer } from '../rendering/PixiRenderer';
import { HandTrackManager, handSlots } from '../tracking/HandTrackManager';
import type { HandSlot } from '../tracking/HandTrackManager';

type GameState = 'TUTOR' | 'HOME' | 'CHARACTER_SELECTION' | 'START_CAMERA' | 'CALIBRATION' | 'PLAYING' | 'SESSION_COMPLETE';
interface ActivePuppet { slot: HandSlot; puppet: PuppetRig; controller: HandPuppetController }
export const slotBounds = { left: { minX: 0.05, maxX: 0.48 }, right: { minX: 0.52, maxX: 0.95 } };
const sessionDuration = 3 * 60 * 1000;

export class GameApp {
  private tutor?: Tutor;
  private detachKelirLight?: () => void;
  private state: GameState = 'HOME';
  private readonly selected: Partial<Record<HandSlot, string>> = {};
  private readonly tracks = new HandTrackManager();
  private readonly handOverlay: HandOverlay;
  private readonly active: ActivePuppet[] = [];
  private session?: CameraSession;
  private generation = 0;
  private pendingStart?: Promise<void>;
  private cleanup?: Promise<void>;
  private timer?: number;
  private readonly calibration = new HandCalibration();
  private deadline = Infinity;
  private lastHand = 0;
  private message = '';
  private lastStatusChange = -Infinity;
  private startup = { percent: 0, label: '' };
  private startupPacer?: ProgressPacer;
  private disposed = false;
  private audio?: HTMLAudioElement;
  private audioMuted = false;

  constructor(private readonly renderer: PixiRenderer, private readonly video: HTMLVideoElement,
    private readonly ui: HTMLElement) {
    this.handOverlay = new HandOverlay(video);
    this.audio = new Audio(backsoundUrl);
    this.audio.loop = true;
    this.audio.volume = 0.5;
    this.addAudioStartListeners();
    this.startAudio();
    renderer.setUpdate((delta, timestamp) => {
      for (const entry of this.active) entry.controller.update(delta, timestamp);
    });
    ui.addEventListener('click', this.onClick);
    this.render();
  }

  private readonly startAudio = (): void => {
    if (this.state === 'TUTOR' || !this.audio || this.audioMuted || !this.audio.paused || this.disposed) return;
    void this.audio.play().catch(() => {
      // Keep interaction listeners so a blocked or interrupted play can be retried.
    });
  };

  private addAudioStartListeners(): void {
    window.addEventListener('pointerdown', this.startAudio, { passive: true });
    window.addEventListener('touchend', this.startAudio, { passive: true });
    window.addEventListener('click', this.startAudio);
    window.addEventListener('keydown', this.startAudio, { passive: true });
  }

  private removeAudioStartListeners(): void {
    window.removeEventListener('pointerdown', this.startAudio);
    window.removeEventListener('touchend', this.startAudio);
    window.removeEventListener('click', this.startAudio);
    window.removeEventListener('keydown', this.startAudio);
  }

  private toggleAudio(): void {
    this.audioMuted = !this.audioMuted;
    if (this.audio) {
      if (this.audioMuted) {
        this.audio.pause();
      } else {
        this.startAudio();
      }
    }
    this.updateAudioButton();
  }

  private updateAudioButton(): void {
    const btn = this.ui.querySelector<HTMLButtonElement>('[data-action="toggle-audio"]');
    if (!btn) return;
    btn.setAttribute('aria-label', this.audioMuted ? 'Nyalakan audio' : 'Matikan audio');
    btn.setAttribute('title', this.audioMuted ? 'Nyalakan audio' : 'Matikan audio');
    btn.classList.toggle('is-muted', this.audioMuted);
    btn.innerHTML = this.audioButtonContent();
  }

  private audioButtonContent(): string {
    if (this.audioMuted) {
      return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg><span class="audio-text"><span class="audio-word">AUDIO </span>OFF</span>`;
    }
    return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg><span class="audio-text"><span class="audio-word">AUDIO </span>ON</span>`;
  }

  private readonly onClick = (event: MouseEvent): void => {
    const button = (event.target as HTMLElement).closest<HTMLButtonElement>('button');
    if (!button || button.disabled || this.cleanup || this.disposed) return;
    const action = button.dataset.action;
    if (action === 'toggle-audio') {
      this.toggleAudio();
      return;
    }
    if (action === 'tutor') this.setState('TUTOR');
    if (action === 'select') this.setState('CHARACTER_SELECTION');
    if (action === 'assign' && this.state === 'CHARACTER_SELECTION') {
      const slot = button.dataset.slot as HandSlot;
      const id = button.dataset.id!;
      if (!handSlots.includes(slot) || !characterCatalog.some(c => c.id === id && c.available)) return;
      const wasSelected = this.selected[slot] === id;
      const previousSlot = handSlots.find(other => this.selected[other] === id);
      for (const other of handSlots) if (this.selected[other] === id) delete this.selected[other];
      if (!wasSelected) this.selected[slot] = id;
      this.message = previousSlot && previousSlot !== slot
        ? `Wayang dipindahkan ke ${slot === 'left' ? 'kiri' : 'kanan'}. Satu tokoh hanya bisa dipilih untuk satu sisi.` : '';
      this.render();
    }
    if (action === 'start') this.start();
    if (action === 'change') void this.finish('CHARACTER_SELECTION');
    if (action === 'home') void this.finish('HOME');
  };

  private start(): void {
    if (this.cleanup || this.pendingStart || this.disposed
      || !['CHARACTER_SELECTION', 'SESSION_COMPLETE'].includes(this.state)) return;
    if (window.matchMedia('(max-width: 767px) and (orientation: portrait)').matches) {
      this.message = 'Putar ponsel ke posisi landscape untuk mulai bermain.';
      this.render();
      return;
    }
    const entries = handSlots.flatMap(slot => {
      const entry = characterCatalog.find(c => c.id === this.selected[slot] && c.available);
      return entry ? [{ slot, definition: entry.definition }] : [];
    });
    if (entries.length < 1 || entries.length > 2) return;
    if (new Set(entries.map(e => e.definition.id)).size !== entries.length) {
      this.message = 'Pilih dua tokoh yang berbeda untuk sisi kiri dan kanan.';
      this.render();
      return;
    }
    const generation = ++this.generation;
    const totalAssets = entries.reduce((sum, { definition }) => sum + PuppetRig.assetCount(definition), 0);
    let loadedAssets = 0;
    this.startup = { percent: 0, label: 'Memuat gambar wayang…' };
    this.startupPacer?.cancel();
    this.startupPacer = createProgressPacer(percent => this.renderStartup(percent));
    this.setState('START_CAMERA');
    this.pendingStart = (async () => {
      try {
        for (const { slot, definition } of entries) {
          const puppet = await PuppetRig.load(definition, () => {
            if (generation === this.generation) this.setStartup(++loadedAssets / totalAssets * 35, 'Memuat gambar wayang…');
          });
          this.active.push({ slot, puppet, controller: new HandPuppetController(puppet,
            this.renderer, this.video, { ...definition.movementBounds, ...slotBounds[slot] }) });
          if (generation !== this.generation) return;
        }
        this.renderer.show(this.active);
        this.session = new CameraSession(this.video, {
          status: message => { this.message = message; this.updateStatus(); },
          progress: (percent, label) => { if (generation === this.generation) this.setStartup(percent, label); },
          ready: () => {
            // Let the bar visibly reach 100% (min. 2 s overall) before calibration starts.
            void this.startupPacer?.finish().then(() => {
              if (generation !== this.generation || this.state !== 'START_CAMERA') return;
              this.lastHand = performance.now();
              this.setState('CALIBRATION');
              this.timer = window.setInterval(() => this.tick(), 250);
            });
          },
          result: (result, timestamp) => this.accept(result, timestamp),
          pause: () => {
            this.calibration.reset();
            for (const entry of this.active) entry.controller.stop();
          },
          error: message => { void this.finish('CHARACTER_SELECTION', message); },
        });
        await this.session.start();
      } catch (error) {
        console.error('Unable to start Wayang:', error);
        if (generation === this.generation) void this.finish('CHARACTER_SELECTION', 'Wayang tidak dapat dimuat. Silakan coba lagi.');
      }
    })().finally(() => { this.pendingStart = undefined; });
  }

  private accept(result: HandLandmarkerResult, timestamp: number): void {
    if (this.state !== 'CALIBRATION' && this.state !== 'PLAYING') return;
    const hands = this.tracks.update(result, timestamp);
    this.handOverlay.draw(hands);
    if (this.active.some(entry => hands[entry.slot])) this.lastHand = timestamp;
    const allPresent = this.active.every(entry => hands[entry.slot]);
    if (this.state === 'CALIBRATION') {
      if (this.calibration.update(allPresent, timestamp)) {
        this.deadline = timestamp + sessionDuration;
        this.setState('PLAYING');
      } else {
        this.message = `${this.calibrationMessage()} ${allPresent ? 'Tahan sebentar…' : ''}`;
        this.updateStatus();
      }
    }
    if (this.state === 'PLAYING') {
      for (const entry of this.active) entry.controller.acceptLandmarks(hands[entry.slot], timestamp);
      this.message = allPresent ? '' : 'Tangan tidak terlihat. Tunjukkan kembali tangan yang dipilih.';
      this.updateStatus();
    }
  }

  private tick(): void {
    const now = performance.now();
    if ((this.state === 'PLAYING' && now >= this.deadline) || now - this.lastHand >= 25000) {
      void this.finish('SESSION_COMPLETE');
      return;
    }
    const timer = this.ui.querySelector('#session-time');
    if (timer && this.state === 'PLAYING') {
      const seconds = Math.max(0, Math.ceil((this.deadline - now) / 1000));
      timer.textContent = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
    }
  }

  private finish(state: GameState, message = ''): Promise<void> {
    if (this.cleanup) return this.cleanup;
    ++this.generation;
    this.startupPacer?.cancel();
    this.startupPacer = undefined;
    window.clearInterval(this.timer);
    this.timer = undefined;
    this.session?.destroy();
    this.session = undefined;
    this.tracks.reset();
    this.handOverlay.clear();
    this.calibration.reset();
    this.deadline = Infinity;
    this.state = state;
    this.message = message;
    const pending = this.pendingStart;
    const keepSelectedTextures = state === 'SESSION_COMPLETE';
    this.cleanup = (async () => {
      await pending;
      this.renderer.show([]);
      for (const entry of this.active) entry.puppet.destroy();
      // Keep the selected textures cached across MAIN LAGI. Release them when
      // leaving the completed session or changing characters.
      const definitions = characterCatalog.filter(c => Object.values(this.selected).includes(c.id)).map(c => c.definition);
      this.active.length = 0;
      if (!keepSelectedTextures) {
        await Promise.allSettled(definitions.map(definition => PuppetRig.unload(definition)));
      }
    })().finally(() => {
      this.cleanup = undefined;
      if (!this.disposed) this.render();
    });
    this.render();
    return this.cleanup;
  }

  private setState(state: GameState, message = ''): void {
    this.state = state;
    this.message = state === 'CALIBRATION' ? this.calibrationMessage() : message;
    this.render();
  }

  private calibrationMessage(): string {
    return this.active.length === 2 ? 'Tunjukkan kedua tangan selama 1,5 detik.'
      : `Tunjukkan tangan ${this.active[0]?.slot === 'left' ? 'kiri' : 'kanan'} selama 1,5 detik.`;
  }

  /** Real startup progress; the pacer decides what is shown. */
  private setStartup(percent: number, label: string): void {
    this.startup.label = label;
    this.ui.querySelector<HTMLElement>('.siap-label')?.replaceChildren(label);
    this.startupPacer?.set(percent);
  }

  private renderStartup(percent: number): void {
    this.startup.percent = percent;
    const value = Math.round(percent);
    const panel = this.ui.querySelector<HTMLElement>('.siap');
    if (!panel) return;
    panel.querySelector<HTMLElement>('.siap-percent')!.textContent = `${value}%`;
    panel.querySelector<HTMLElement>('.siap-fill')!.style.width = `${value}%`;
    panel.querySelector<HTMLElement>('[role="progressbar"]')!.setAttribute('aria-valuenow', String(value));
  }

  private startupPanel(): string {
    const value = Math.round(this.startup.percent);
    return `<section class="siap" aria-labelledby="siap-title">
      <h2 id="siap-title">Menyiapkan panggung</h2>
      <p class="siap-percent" aria-hidden="true">${value}%</p>
      <div class="siap-track" role="progressbar" aria-label="Progres persiapan panggung" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${value}">
        <span class="siap-fill" style="width:${value}%"></span>
      </div>
      <p class="siap-label" aria-live="polite">${this.startup.label}</p>
    </section>`;
  }

  private updateStatus(): void {
    const status = this.ui.querySelector<HTMLElement>('#camera-status');
    const text = this.message.trim();
    // Called on every tracking result: only touch the DOM when the instruction changes.
    if (!status || status.textContent === text) return;
    status.textContent = text;
    const now = performance.now();
    // Fade up on change; skip when instructions flicker faster than the animation.
    if (text && now - this.lastStatusChange > 450 && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      status.animate(
        [{ opacity: 0, translate: '0 12px' }, { opacity: 1, translate: '0 0' }],
        { duration: 320, easing: 'cubic-bezier(0.2, 0.8, 0.2, 1)' },
      );
    }
    this.lastStatusChange = now;
  }

  private render(): void {
    this.tutor?.destroy(); this.tutor = undefined;
    this.detachKelirLight?.(); this.detachKelirLight = undefined;
    if (this.state === 'TUTOR') {
      this.audio?.pause();
      this.ui.className = 'screen screen--tutor';
      this.ui.parentElement?.classList.remove('game-active');
      this.tutor = new Tutor(this.ui);
      return;
    }
    this.startAudio();
    const blocked = this.cleanup ? 'disabled' : '';
    let content = '';
    if (this.state === 'HOME') {
      const cast = characterCatalog.map((entry, index) => {
        const src = entry.thumbnail ?? entry.definition.assets.body;
        return `<figure class="kelir-wayang kelir-wayang--${index + 1}">
          <img class="kelir-shadow" src="${src}" alt="" aria-hidden="true" decoding="async" draggable="false">
          <img class="kelir-puppet" src="${src}" alt="${entry.name}" decoding="async" draggable="false">
          <figcaption>${entry.name}</figcaption>
        </figure>`;
      }).join('');
      content = `<div class="home">
        <header class="home-bar">
          <span class="brand-mark" aria-hidden="true">WB</span><span class="home-brand">Wayang Bali</span>
        </header>
        <section class="kelir" aria-labelledby="home-title">
          <div class="kelir-copy">
            <h1 id="home-title">Hidupkan cerita lewat gerakmu.</h1>
            <p class="kelir-lead">Pilih tokoh, gerakkan tangan, dan mainkan Wayang Bali langsung dari kamera perangkatmu.</p>
            <div class="kelir-actions">
              <button class="primary-button" data-action="select" ${blocked}>Pilih wayang</button>
              <button class="tutor-entry" data-action="tutor">${tutorIcon} Tanya AI Tutor</button>
            </div>
            <p class="privacy-note">Video kamera diproses langsung di perangkat dan tidak disimpan.</p>
          </div>
          <div class="kelir-stage" role="img" aria-label="Empat tokoh Wayang Bali di depan kelir">${cast}</div>
          <div class="gedebong" aria-hidden="true"></div>
        </section>
        <section class="home-steps" aria-labelledby="steps-title">
          <h2 id="steps-title">Cara bermain</h2>
          <ol>
            <li><strong>Pilih tokoh</strong><span>Satu atau dua wayang, untuk tangan kiri dan kanan.</span></li>
            <li><strong>Tunjukkan tangan</strong><span>Tahan di depan kamera sebentar sampai wayang siap.</span></li>
            <li><strong>Mainkan</strong><span>Telapak menggerakkan badan, telunjuk dan jari tengah menggerakkan lengan. Satu sesi 3 menit.</span></li>
          </ol>
        </section>
        <footer class="home-foot">
          <a href="https://www.youtube.com/watch?v=LvChlFqEYRo" target="_blank" rel="noopener noreferrer">Musik latar: &ldquo;Astadi Jaya&rdquo; (YouTube)</a>
          <p>Aset Wayang : Ngurah Made Arya Asmara Jaya, M.Sn (Seniman Dalang Pewayangan Bali)</p>
        </footer>
      </div>`;
    }
    if (this.state === 'CHARACTER_SELECTION') {
      const cards = characterCatalog.map(entry => {
        const selectedSlot = handSlots.find(slot => this.selected[slot] === entry.id);
        const src = entry.thumbnail ?? entry.definition.assets.body;
        // Face the puppet toward the centre of the stage for its slot.
        const flip = selectedSlot && selectedSlot === entry.definition.artworkFacing ? ' is-flipped' : '';
        return `<article class="pilih-card${selectedSlot ? ` is-selected is-${selectedSlot}` : ''}" aria-label="${entry.name}">
          <div class="pilih-tile${flip}">
            ${selectedSlot ? `<span class="pilih-chip">${selectedSlot === 'left' ? 'Kiri' : 'Kanan'}</span>` : ''}
            <img class="pilih-shadow" src="${src}" alt="" aria-hidden="true" loading="lazy" decoding="async" draggable="false">
            <img class="pilih-puppet" src="${src}" alt="" loading="lazy" decoding="async" draggable="false">
          </div>
          <h2>${entry.name}</h2>
          <div class="pilih-hands" role="group" aria-label="Tangan untuk ${entry.name}">${handSlots.map(slot => `<button data-action="assign" data-id="${entry.id}" data-slot="${slot}"
            aria-pressed="${this.selected[slot] === entry.id}" aria-label="${entry.name} untuk tangan ${slot === 'left' ? 'kiri' : 'kanan'}"
            ${!entry.available || this.cleanup ? 'disabled' : ''}>${slot === 'left' ? 'Kiri' : 'Kanan'}</button>`).join('')}</div>
        </article>`;
      }).join('');
      content = `<div class="pilih">
        <header class="pilih-header">
          <button class="pilih-back" data-action="home" ${blocked}><span aria-hidden="true">←</span> Menu utama</button>
          <button class="pilih-tutor" data-action="tutor">${tutorIcon} Tanya AI Tutor</button>
          <div class="pilih-intro">
            <h1>Pilih wayang</h1>
            <p>Pilih satu atau dua tokoh, lalu tentukan tangan yang memainkannya. Tokoh yang sama hanya bisa di satu sisi.</p>
          </div>
        </header>
        <div class="pilih-grid">${cards}</div>
        <div class="pilih-dock">
          <div class="pilih-slots">${this.selectionSlots()}</div>
          <button class="primary-button" data-action="start" ${!Object.values(this.selected).length || this.cleanup ? 'disabled' : ''}>Mulai bermain</button>
        </div>
      </div>`;
    }
    if (['START_CAMERA', 'CALIBRATION', 'PLAYING'].includes(this.state)) {
      const phase = this.state === 'START_CAMERA' ? 'Menyiapkan panggung'
        : this.state === 'CALIBRATION' ? 'Kalibrasi gerak' : 'Sedang bermain';
      content = `<div class="game-hud glass-panel">
        <button class="hud-button" data-action="home"><span aria-hidden="true">←</span> MENU UTAMA</button>
        <div class="game-phase"><span class="live-dot" aria-hidden="true"></span><strong>${phase}</strong><small>${this.formattedSelectionSummary()}</small></div>
        <button class="hud-button audio-toggle ${this.audioMuted ? 'is-muted' : ''}" data-action="toggle-audio" aria-label="${this.audioMuted ? 'Nyalakan audio' : 'Matikan audio'}" title="${this.audioMuted ? 'Nyalakan audio' : 'Matikan audio'}">${this.audioButtonContent()}</button>
        ${this.state === 'PLAYING' ? '<span id="session-time" aria-label="Waktu tersisa">3:00</span>' : '<span class="hud-emblem" aria-hidden="true">WB</span>'}
        <button class="hud-button" data-action="change">GANTI WAYANG</button>
      </div>${this.state === 'START_CAMERA' ? this.startupPanel() : ''}${this.orientationGuard()}`;
    }
    if (this.state === 'SESSION_COMPLETE') {
      const names = handSlots.map(slot => characterCatalog.find(c => c.id === this.selected[slot])?.name).filter(Boolean);
      // The puppets just played, facing each other; all four if none are selected.
      const chosen = handSlots.flatMap(slot => {
        const entry = characterCatalog.find(c => c.id === this.selected[slot]);
        return entry ? [{ slot, entry }] : [];
      });
      const shown = chosen.length ? chosen : characterCatalog.map(entry => ({ slot: undefined, entry }));
      const cast = shown.map(({ slot, entry }, index) => {
        const src = entry.thumbnail ?? entry.definition.assets.body;
        const flip = slot && slot === entry.definition.artworkFacing ? ' is-flipped' : '';
        return `<figure class="selesai-wayang selesai-wayang--${shown.length}-${index + 1}${flip}">
          <img class="selesai-shadow" src="${src}" alt="" decoding="async" draggable="false">
          <img class="selesai-puppet" src="${src}" alt="" decoding="async" draggable="false">
        </figure>`;
      }).join('');
      const played = names.length ? ` Terima kasih sudah memainkan ${names.join(' dan ')}.` : ' Terima kasih sudah menghidupkan kisah Wayang Bali.';
      content = `<div class="selesai">
        <section class="selesai-kelir" aria-labelledby="selesai-title">
          <div class="selesai-stage" aria-hidden="true">${cast}</div>
          <div class="selesai-gedebong" aria-hidden="true"></div>
          <div class="selesai-copy">
            <h1 id="selesai-title">Sesi selesai</h1>
            <p>Lakon telah usai dan kelir kembali tenang.${played}</p>
            <div class="selesai-actions">
              <button class="primary-button" data-action="start" ${blocked}>Main lagi</button>
              <button data-action="change" ${blocked}>Ganti wayang</button>
              <button data-action="home" ${blocked}>Menu utama</button>
            </div>
          </div>
        </section>
      </div>`;
    }
    const isPlaying = !['HOME', 'CHARACTER_SELECTION', 'SESSION_COMPLETE'].includes(this.state);
    this.ui.className = isPlaying ? 'camera-controls game-ui' : `screen screen--${this.state.toLowerCase()}`;
    this.ui.parentElement?.classList.toggle('game-active', isPlaying);
    this.ui.innerHTML = `${content}<p id="camera-status" role="status" aria-live="polite"></p>`;
    if (this.state === 'HOME') this.detachKelirLight = attachKelirLight(this.ui);
    this.updateStatus();
  }

  private selectionSlots(): string {
    return handSlots.map(slot => {
      const character = characterCatalog.find(c => c.id === this.selected[slot]);
      const flip = character && slot === character.definition.artworkFacing ? ' is-flipped' : '';
      const image = character ? `<img class="${flip.trim()}" src="${character.thumbnail ?? character.definition.assets.body}" alt="" decoding="async">` : '';
      return `<div class="pilih-slot pilih-slot--${slot}${character ? ' is-filled' : ''}">
        <span class="pilih-slot-art" aria-hidden="true">${image}</span>
        <span class="pilih-slot-text"><small>Tangan ${slot === 'left' ? 'kiri' : 'kanan'}</small><strong>${character?.name ?? 'Belum dipilih'}</strong></span>
      </div>`;
    }).join('');
  }

  private formattedSelectionSummary(): string {
    return handSlots.map(slot => `Tangan ${slot === 'left' ? 'kiri' : 'kanan'}: ${characterCatalog.find(c => c.id === this.selected[slot])?.name ?? '—'}`).join(' · ');
  }

  private orientationGuard(): string {
    return `<aside class="orientation-guard" role="alert" aria-label="Orientasi landscape diperlukan">
      <div class="phone-rotate" aria-hidden="true">↻</div><h2>Putar ponselmu</h2>
      <p>Permainan Wayang menggunakan orientasi landscape agar panggung dan gerakan tangan terlihat penuh.</p>
    </aside>`;
  }

  async destroy(): Promise<void> {
    this.disposed = true;
    this.tutor?.destroy();
    this.detachKelirLight?.();
    this.handOverlay.destroy();
    this.removeAudioStartListeners();
    if (this.audio) {
      this.audio.pause();
      this.audio.src = '';
      this.audio = undefined;
    }
    this.ui.removeEventListener('click', this.onClick);
    this.ui.parentElement?.classList.remove('game-active');
    await this.finish('HOME');
  }
}
