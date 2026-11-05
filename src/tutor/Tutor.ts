import { VoiceRecorder } from './VoiceRecorder';
import type { VoiceInput } from './VoiceRecorder';
import { characterCatalog } from '../puppet/characters/catalog';

export const tutorIcon = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 3v3M9 3h6M5 7h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Z"/><path d="M8 16h8M8 11v2M16 11v2"/></svg>';

export class Tutor {
  private readonly recorder: VoiceRecorder;
  private request?: AbortController;
  private recording = false;
  private busy = false;
  private disposed = false;
  private lastAnswer = '';
  private lastAudio = '';
  private playback?: HTMLAudioElement;
  private voiceGeneration = 0;
  private readonly input: HTMLTextAreaElement;
  private readonly status: HTMLElement;
  private readonly log: HTMLElement;
  private readonly mic: HTMLButtonElement;
  private readonly send: HTMLButtonElement;
  private readonly speakingBanner: HTMLElement;
  private readonly speakingBadge: HTMLElement;
  private readonly speakingTime: HTMLElement;
  private readonly speakingHint: HTMLElement;
  private readonly waveBars: HTMLElement[];

  constructor(private readonly host: HTMLElement) {
    host.innerHTML = `<section class="page-shell tutor-shell">
      <header class="tutor-header"><button data-action="home">← MENU UTAMA</button><div><p class="eyebrow">Belajar bersama</p><h1>${tutorIcon} AI Tutor Wayang Bali</h1><p>Tanyakan tokoh, jenis, cerita, dan sejarah wayang di Bali lewat teks atau suara.</p></div></header>
      <div class="tutor-cast" aria-label="Galeri wayang Bali">${characterCatalog.map(c => `<figure class="tutor-character"><img src="${c.thumbnail}" alt=""/><figcaption>${c.name}</figcaption></figure>`).join('')}</div>
      <section class="tutor-chat glass-panel" aria-label="Percakapan tutor">
        <div class="tutor-log" role="log" aria-live="polite"><p class="tutor-bubble">Om Swastiastu! Langsung tanyakan apa saja tentang wayang di Bali, termasuk tokoh, jenis, sejarah, cerita, dan nilai budayanya.</p></div>
        <div class="tutor-suggestions"><button data-question="Bagaimana sejarah wayang di Bali?">Sejarah wayang Bali</button><button data-question="Apa saja jenis wayang di Bali?">Jenis wayang Bali</button><button data-question="Apa itu Wayang Lemah di Bali?">Wayang Lemah</button></div>
        <div class="tutor-speaking-banner is-hidden" id="tutor-speaking-banner" hidden aria-live="polite">
          <div class="tutor-speaking-header">
            <span class="tutor-speaking-badge" id="tutor-speaking-badge"><span class="tutor-speaking-dot" aria-hidden="true"></span> Mendengarkan…</span>
            <span class="tutor-speaking-time" id="tutor-speaking-time">Sisa 15 dtk</span>
          </div>
          <div class="tutor-wave" id="tutor-wave" aria-hidden="true">
            <span class="tutor-wave-bar"></span>
            <span class="tutor-wave-bar"></span>
            <span class="tutor-wave-bar"></span>
            <span class="tutor-wave-bar"></span>
            <span class="tutor-wave-bar"></span>
            <span class="tutor-wave-bar"></span>
            <span class="tutor-wave-bar"></span>
          </div>
          <p class="tutor-speaking-hint" id="tutor-speaking-hint">Silakan bicara sekarang, mikrofon aktif…</p>
        </div>
        <form class="tutor-form"><label for="tutor-input">Pertanyaan tentang wayang Bali</label><textarea id="tutor-input" rows="2" maxlength="300" placeholder="Contoh: Bagaimana sejarah Wayang Gambuh di Bali?" required></textarea>
        <p class="tutor-status" role="status" aria-live="polite"></p><div class="tutor-tools"><span id="tutor-count">0/300</span><button type="button" id="tutor-mic" aria-pressed="false"><span aria-hidden="true">🎙</span> Bicara</button><button class="primary-button" id="tutor-send" type="submit">Kirim ↑</button></div></form>
        <div class="tutor-voice"><label><input type="checkbox" id="tutor-voice" checked> Bacakan jawaban</label><button id="tutor-replay" disabled>Dengarkan ulang</button><button id="tutor-stop">Hentikan suara</button></div>
        <small>v0.2.0 • Hanya seputar wayang Bali • Jawaban singkat • AI dapat keliru. Rekaman maks. 15 detik dikirim ke Gemini atau OpenAI saat selesai. Suara jawaban dibuat oleh AI atau pembaca suara perangkat.</small>
      </section></section>`;
    this.input = host.querySelector('#tutor-input')!;
    this.status = host.querySelector('.tutor-status')!;
    this.log = host.querySelector('.tutor-log')!;
    this.mic = host.querySelector('#tutor-mic')!;
    this.send = host.querySelector('#tutor-send')!;
    this.speakingBanner = host.querySelector('#tutor-speaking-banner')!;
    this.speakingBadge = host.querySelector('#tutor-speaking-badge')!;
    this.speakingTime = host.querySelector('#tutor-speaking-time')!;
    this.speakingHint = host.querySelector('#tutor-speaking-hint')!;
    this.waveBars = Array.from(host.querySelectorAll('.tutor-wave-bar'));

    // Guarantee banner is hidden on initial load
    this.speakingBanner.hidden = true;
    this.speakingBanner.classList.add('is-hidden');

    this.recorder = new VoiceRecorder(
      message => { if (!this.disposed) this.status.textContent = message; },
      (active, pending) => this.setRecording(active, pending),
      audio => { if (!this.disposed) void this.submit(audio); },
      (level, speaking) => this.onVolume(level, speaking),
      secondsLeft => this.onCountdown(secondsLeft),
    );

    if (!VoiceRecorder.supported()) {
      this.mic.disabled = true;
      this.status.textContent = 'Mikrofon tidak tersedia. Buka situs melalui HTTPS di browser terbaru atau gunakan teks.';
    }
    host.querySelector('form')!.addEventListener('submit', event => { event.preventDefault(); void this.submit(); });
    this.input.addEventListener('input', () => this.count());
    host.addEventListener('click', this.onClick);
    document.addEventListener('visibilitychange', this.onVisibility);
    host.querySelector('#tutor-voice')!.addEventListener('change', () => this.stopPlayback());
  }

  private onVolume(level: number, speaking: boolean): void {
    if (this.disposed || !this.recording) return;
    if (speaking) {
      this.speakingBadge.className = 'tutor-speaking-badge is-speaking';
      this.speakingBadge.innerHTML = '<span class="tutor-speaking-dot" aria-hidden="true"></span> Suara Terdengar';
      this.speakingHint.textContent = 'Suara terdeteksi! Silakan lanjutkan pertanyaan…';
      this.speakingHint.classList.add('is-speaking');
    } else {
      this.speakingBadge.className = 'tutor-speaking-badge';
      this.speakingBadge.innerHTML = '<span class="tutor-speaking-dot" aria-hidden="true"></span> Mendengarkan…';
      this.speakingHint.textContent = 'Silakan bicara sekarang, mikrofon aktif…';
      this.speakingHint.classList.remove('is-speaking');
    }
    const factors = [0.3, 0.6, 0.9, 1.2, 0.9, 0.6, 0.3];
    this.waveBars.forEach((bar, idx) => {
      const base = factors[idx] ?? 0.5;
      const scale = Math.max(0.2, Math.min(2.8, (base * level * 2.2) + 0.25));
      bar.style.transform = `scaleY(${scale.toFixed(2)})`;
      bar.classList.toggle('is-speaking', speaking);
    });
  }

  private onCountdown(secondsLeft: number): void {
    if (this.disposed) return;
    this.speakingTime.textContent = `Sisa ${secondsLeft} dtk`;
  }

  private count(): void {
    this.host.querySelector('#tutor-count')!.textContent = `${this.input.value.length}/300`;
  }

  private readonly onVisibility = (): void => {
    if (document.hidden) {
      if (this.recording) this.status.textContent = 'Rekaman dibatalkan karena halaman ditinggalkan.';
      this.stopVoice();
    }
  };

  private stopVoice(): void {
    this.recorder.cancel();
    this.setRecording(false, false);
    this.stopPlayback();
  }

  private setRecording(value: boolean, pending = false): void {
    this.recording = value;
    this.mic.setAttribute('aria-pressed', String(value));
    if (pending) {
      this.mic.disabled = true;
      this.mic.innerHTML = '<span aria-hidden="true">⏳</span> Menyiapkan…';
      this.speakingBanner.hidden = false;
      this.speakingBanner.classList.remove('is-hidden');
      this.speakingBadge.className = 'tutor-speaking-badge is-preparing';
      this.speakingBadge.innerHTML = '<span aria-hidden="true">⏳</span> Menyiapkan Mikrofon';
      this.speakingHint.textContent = 'Menghubungkan mikrofon…';
      this.speakingTime.textContent = 'Sisa 15 dtk';
      this.input.disabled = true;
    } else if (value) {
      this.mic.disabled = false;
      this.mic.innerHTML = '<span class="tutor-rec-dot" aria-hidden="true"></span> Selesai & kirim';
      this.speakingBanner.hidden = false;
      this.speakingBanner.classList.remove('is-hidden');
      this.speakingBadge.className = 'tutor-speaking-badge';
      this.speakingBadge.innerHTML = '<span class="tutor-speaking-dot" aria-hidden="true"></span> Mendengarkan…';
      this.speakingHint.textContent = 'Silakan bicara sekarang, mikrofon aktif…';
      this.input.disabled = true;
    } else {
      this.mic.disabled = this.busy || !VoiceRecorder.supported();
      this.mic.innerHTML = '<span aria-hidden="true">🎙</span> Bicara';
      this.speakingBanner.hidden = true;
      this.speakingBanner.classList.add('is-hidden');
      this.input.disabled = false;
      this.waveBars.forEach(bar => {
        bar.style.transform = '';
        bar.classList.remove('is-speaking');
      });
    }
    this.send.disabled = value || pending || this.busy;
  }

  private readonly onClick = (event: MouseEvent): void => {
    const button = (event.target as HTMLElement).closest<HTMLButtonElement>('button');
    if (!button || button.disabled) return;
    if (button.dataset.question && !this.busy) {
      this.input.value = button.dataset.question;
      this.count();
      void this.submit();
    }
    if (button.id === 'tutor-mic' && !this.busy) {
      if (this.recording) {
        this.recorder.finish();
        return;
      }
      this.stopPlayback();
      void this.recorder.start();
    }
    if (button.id === 'tutor-replay') this.speak(this.lastAnswer);
    if (button.id === 'tutor-stop') {
      this.stopVoice();
      this.status.textContent = 'Suara dihentikan.';
    }
  };

  private stopPlayback(): void {
    this.voiceGeneration++;
    if (this.playback) {
      this.playback.pause();
      this.playback.removeAttribute('src');
      this.playback.load();
      this.playback = undefined;
    }
    window.speechSynthesis?.cancel();
  }

  private speak(text: string): void {
    this.stopPlayback();
    if (this.disposed || document.hidden) return;
    if (this.lastAudio) {
      const playback = new Audio(this.lastAudio);
      this.playback = playback;
      const generation = this.voiceGeneration;
      void playback.play().catch(() => {
        if (this.disposed || document.hidden || generation !== this.voiceGeneration) return;
        this.stopPlayback();
        this.speakDevice(text);
      });
      return;
    }
    this.speakDevice(text);
  }

  private speakDevice(text: string): void {
    if (!('speechSynthesis' in window)) {
      this.status.textContent = 'Pembaca suara tidak tersedia. Jawaban tetap dapat dibaca.';
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'id-ID';
    utterance.rate = 0.95;
    const voice = window.speechSynthesis.getVoices().find(v => v.lang.startsWith('id'));
    if (voice) utterance.voice = voice;
    utterance.onerror = () => {
      if (!this.disposed) this.status.textContent = 'Pembaca suara tidak tersedia. Jawaban tetap dapat dibaca.';
    };
    window.speechSynthesis.speak(utterance);
  }

  private bubble(text: string, user = false): HTMLElement {
    const p = document.createElement('p');
    p.className = `tutor-bubble${user ? ' tutor-bubble--user' : ''}`;
    p.textContent = text;
    this.log.append(p);
    while (this.log.children.length > 12) this.log.firstElementChild?.remove();
    this.log.scrollTop = this.log.scrollHeight;
    return p;
  }

  private async submit(audio?: VoiceInput): Promise<void> {
    const message = this.input.value.trim();
    if (this.busy || (!audio && (!message || message.length > 300)) || this.disposed) return;
    this.stopVoice();
    this.busy = true;
    this.send.disabled = true;
    this.mic.disabled = true;
    this.host.querySelectorAll<HTMLButtonElement>('[data-question]').forEach(b => { b.disabled = true; });

    // Show initial user bubble in the chat log
    let userBubbleEl: HTMLElement | undefined;
    if (audio) {
      userBubbleEl = this.bubble('🎙 Mendengarkan rekaman suara…', true);
    } else {
      userBubbleEl = this.bubble(message, true);
    }

    this.status.textContent = 'Tutor sedang menjawab…';
    const voiceGeneration = this.voiceGeneration;
    this.request = new AbortController();
    const timeout = window.setTimeout(() => this.request?.abort(), 85000);

    try {
      const response = await fetch('/tutor.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...(audio ? { audio } : { message }),
          speak: this.host.querySelector<HTMLInputElement>('#tutor-voice')!.checked,
        }),
        signal: this.request.signal,
      });

      const data: unknown = await response.json();
      if (typeof data !== 'object' || data === null) throw new Error('Jawaban belum tersedia.');
      if (!response.ok || !('answer' in data) || typeof data.answer !== 'string' || !data.answer.trim()) {
        throw new Error('error' in data && typeof data.error === 'string' ? data.error : 'Jawaban belum tersedia.');
      }
      if (this.disposed) return;

      // When audio is used, update the user's chat bubble with the recognized speech
      if (audio && userBubbleEl) {
        if ('question' in data && typeof data.question === 'string' && data.question.trim()) {
          userBubbleEl.textContent = `🎙 "${data.question.trim()}"`;
        } else {
          userBubbleEl.textContent = '🎙 Pertanyaan suara';
        }
      }

      this.lastAudio = '';
      if ('audio' in data && typeof data.audio === 'object' && data.audio !== null
        && 'mimeType' in data.audio && data.audio.mimeType === 'audio/mpeg'
        && 'data' in data.audio && typeof data.audio.data === 'string'
        && data.audio.data.length <= 4_000_000 && /^[A-Za-z0-9+/]+={0,2}$/.test(data.audio.data)) {
        this.lastAudio = `data:audio/mpeg;base64,${data.audio.data}`;
      }
      this.lastAnswer = data.answer;
      this.bubble(data.answer);
      this.input.value = '';
      this.count();
      this.status.textContent = '';
      this.host.querySelector<HTMLButtonElement>('#tutor-replay')!.disabled = !this.lastAudio && !('speechSynthesis' in window);
      if (this.host.querySelector<HTMLInputElement>('#tutor-voice')!.checked && !document.hidden && voiceGeneration === this.voiceGeneration) {
        this.speak(data.answer);
      }
    } catch (error) {
      if (audio && userBubbleEl && userBubbleEl.textContent === '🎙 Mendengarkan rekaman suara…') {
        userBubbleEl.textContent = '🎙 Rekaman suara (gagal diproses)';
      }
      if (!this.disposed) {
        this.status.textContent = error instanceof Error && error.name !== 'AbortError' ? error.message : 'Koneksi terputus atau terlalu lama. Coba kirim lagi.';
      }
    } finally {
      window.clearTimeout(timeout);
      this.busy = false;
      if (!this.disposed) {
        this.send.disabled = false;
        this.mic.disabled = !VoiceRecorder.supported();
        this.host.querySelectorAll<HTMLButtonElement>('[data-question]').forEach(b => { b.disabled = false; });
      }
    }
  }

  destroy(): void {
    this.disposed = true;
    this.request?.abort();
    this.stopVoice();
    this.lastAudio = '';
    this.host.removeEventListener('click', this.onClick);
    document.removeEventListener('visibilitychange', this.onVisibility);
  }
}
