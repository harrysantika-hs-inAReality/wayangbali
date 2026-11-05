export interface VoiceInput { data: string; mimeType: string }

/** One bounded recording; late permission grants and cancelled recordings are discarded. */
export class VoiceRecorder {
  private recorder?: MediaRecorder;
  private stream?: MediaStream;
  private timer?: number;
  private countdownTimer?: number;
  private audioCtx?: AudioContext;
  private analyser?: AnalyserNode;
  private animId?: number;
  private generation = 0;
  private pending = false;
  private stopping = false;

  get active(): boolean { return this.pending || this.recorder?.state === 'recording'; }
  static supported(): boolean { return window.isSecureContext && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== 'undefined'; }

  constructor(
    private readonly status: (message: string) => void,
    private readonly changed: (active: boolean, pending?: boolean) => void,
    private readonly complete: (audio: VoiceInput) => void,
    private readonly volume?: (level: number, speaking: boolean) => void,
    private readonly countdown?: (secondsLeft: number) => void,
  ) {}

  async start(): Promise<void> {
    if (this.active) return;
    const generation = ++this.generation;
    this.pending = true;
    this.stopping = false;
    this.changed(true, true);
    this.status('Izinkan mikrofon pada dialog browser…');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          channelCount: 1,
        },
        video: false,
      });

      if (generation !== this.generation) {
        stream.getTracks().forEach(t => t.stop());
        return;
      }

      this.stream = stream;
      // Prefer WebM Opus for Chrome/Edge/Firefox/Android; fall back to MP4 for iOS Safari.
      const mimeType = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus'].find(type => MediaRecorder.isTypeSupported(type));
      if (!mimeType) throw new Error('Format rekaman tidak didukung. Perbarui browser atau gunakan teks.');

      const recorder = new MediaRecorder(stream, { mimeType, audioBitsPerSecond: 64000 });
      this.recorder = recorder;
      const chunks: Blob[] = [];

      recorder.ondataavailable = event => {
        if (event.data.size) chunks.push(event.data);
      };

      recorder.onerror = () => {
        if (generation === this.generation) {
          this.cancel();
          this.status('Rekaman gagal. Coba lagi atau gunakan teks.');
        }
      };

      recorder.onstop = () => {
        if (generation !== this.generation) return;
        this.release();
        this.recorder = undefined;
        this.changed(false, false);
        const blob = new Blob(chunks, { type: mimeType });
        if (blob.size < 100) {
          this.status('Rekaman kosong. Tekan Bicara dan coba lagi.');
          return;
        }
        if (blob.size > 262144) {
          this.status('Rekaman terlalu besar. Coba bicara lebih singkat.');
          return;
        }
        const reader = new FileReader();
        reader.onload = () => {
          if (generation === this.generation) {
            this.complete({
              data: String(reader.result).split(',')[1],
              mimeType: mimeType.split(';')[0],
            });
          }
        };
        reader.onerror = () => {
          if (generation === this.generation) this.status('Rekaman tidak dapat dibaca. Coba lagi.');
        };
        reader.readAsDataURL(blob);
      };

      // Set up volume detection for speech animation
      this.setupAnalyser(stream);

      // Start recording with 250ms chunks for reliable flushing on Safari/Chrome
      recorder.start(250);
      this.pending = false;
      this.changed(true, false);
      this.status('● Merekam: Silakan bicara sekarang, lalu tekan Selesai & kirim.');

      // Start 15s countdown
      this.startCountdown(15);
    } catch (error) {
      if (generation !== this.generation) return;
      this.cancel();
      const name = error instanceof Error ? error.name : '';
      this.status(name === 'NotAllowedError' ? 'Mikrofon diblokir. Izinkan mikrofon untuk browser di Pengaturan perangkat dan izin situs, lalu coba lagi.'
        : name === 'NotFoundError' ? 'Mikrofon tidak ditemukan. Sambungkan mikrofon atau gunakan teks.'
        : name === 'NotReadableError' ? 'Mikrofon sedang dipakai aplikasi lain. Tutup aplikasi tersebut lalu coba lagi.'
        : error instanceof Error ? error.message : 'Mikrofon gagal dibuka. Coba lagi atau gunakan teks.');
    }
  }

  private setupAnalyser(stream: MediaStream): void {
    try {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      this.audioCtx = ctx;
      if (ctx.state === 'suspended') void ctx.resume();

      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 128;
      analyser.smoothingTimeConstant = 0.35;
      source.connect(analyser);
      this.analyser = analyser;

      const data = new Uint8Array(analyser.frequencyBinCount);
      const sample = (): void => {
        if (!this.analyser || this.recorder?.state !== 'recording') return;
        this.analyser.getByteFrequencyData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i++) {
          sum += data[i];
        }
        const avg = sum / data.length;
        const normalized = Math.min(1, avg / 70);
        const speaking = normalized > 0.08;
        this.volume?.(normalized, speaking);
        this.animId = requestAnimationFrame(sample);
      };
      this.animId = requestAnimationFrame(sample);
    } catch {
      // AudioContext failure should not prevent recording
    }
  }

  private cleanupAnalyser(): void {
    if (this.animId !== undefined) {
      cancelAnimationFrame(this.animId);
      this.animId = undefined;
    }
    if (this.audioCtx) {
      void this.audioCtx.close().catch(() => {});
      this.audioCtx = undefined;
    }
    this.analyser = undefined;
  }

  private startCountdown(durationSec: number): void {
    let remaining = durationSec;
    this.countdown?.(remaining);
    this.countdownTimer = window.setInterval(() => {
      remaining--;
      if (remaining >= 0) {
        this.countdown?.(remaining);
      }
      if (remaining <= 0) {
        window.clearInterval(this.countdownTimer);
        this.countdownTimer = undefined;
        this.finish();
      }
    }, 1000);
  }

  finish(): void {
    if (this.stopping) return;
    if (this.pending) {
      this.cancel();
      this.status('Permintaan mikrofon dibatalkan. Tekan Bicara untuk mencoba lagi.');
      return;
    }
    if (this.recorder?.state === 'recording') {
      this.stopping = true;
      this.status('Menyiapkan rekaman…');
      // Buffer 250ms to ensure the trailing syllable is flushed into chunks
      window.setTimeout(() => {
        if (this.recorder?.state === 'recording') {
          this.recorder.stop();
        }
      }, 250);
    }
  }

  private release(): void {
    window.clearTimeout(this.timer);
    if (this.countdownTimer !== undefined) {
      window.clearInterval(this.countdownTimer);
      this.countdownTimer = undefined;
    }
    this.cleanupAnalyser();
    this.stream?.getTracks().forEach(t => t.stop());
    this.stream = undefined;
    this.stopping = false;
  }

  cancel(): void {
    ++this.generation;
    this.pending = false;
    this.stopping = false;
    if (this.recorder?.state === 'recording') this.recorder.stop();
    this.recorder = undefined;
    this.release();
    this.changed(false, false);
  }
}
