export class CameraManager {
  private stream?: MediaStream;

  constructor(
    readonly video: HTMLVideoElement,
    private readonly onEnded: () => void,
  ) {}

  async start(signal: AbortSignal): Promise<void> {
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      throw new Error('Kamera memerlukan koneksi HTTPS dan browser yang didukung.');
    }
    try {
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: {
            facingMode: { ideal: 'user' },
            width: { ideal: 640 },
            height: { ideal: 480 },
            frameRate: { ideal: 24, max: 30 },
          },
        });
      } catch (error) {
        // Older Safari and some Android camera drivers reject supported cameras
        // when optional frame-rate constraints cannot be satisfied.
        if (!(error instanceof DOMException)
          || (error.name !== 'OverconstrainedError' && error.name !== 'ConstraintNotSatisfiedError')) throw error;
        stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: { facingMode: { ideal: 'user' }, width: { ideal: 640 }, height: { ideal: 480 } },
        });
      }
      // Permission may resolve after navigation or cancellation.
      if (signal.aborted) {
        stream.getTracks().forEach((track) => track.stop());
        signal.throwIfAborted();
      }
      this.stream = stream;
      stream.getVideoTracks().forEach((track) => {
        track.addEventListener('ended', this.onEnded);
      });
      // This DOM video is both the visible preview and the MediaPipe input.
      this.video.autoplay = true;
      this.video.muted = true;
      this.video.playsInline = true;
      this.video.hidden = false;
      this.video.srcObject = stream;
      await this.video.play();
      await this.waitForPlayableFrame(signal);
      signal.throwIfAborted();
      if (!this.video.isConnected || this.video.srcObject !== stream
        || this.video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA
        || this.video.videoWidth <= 0 || this.video.videoHeight <= 0) {
        throw new Error('Kamera tidak menampilkan gambar. Periksa kamera lalu coba lagi.');
      }
    } catch (error) {
      if (signal.aborted) throw error;
      this.stop();
      if (error instanceof DOMException) {
        if (error.name === 'NotAllowedError' || error.name === 'SecurityError') {
          throw new Error('Izin kamera ditolak. Izinkan akses kamera di browser, lalu coba lagi.');
        }
        if (error.name === 'NotFoundError') throw new Error('Kamera tidak ditemukan.');
        if (error.name === 'NotReadableError') {
          throw new Error('Kamera tidak tersedia atau sedang dipakai aplikasi lain.');
        }
      }
      throw new Error('Kamera tidak dapat dimulai. Periksa kamera lalu coba lagi.', { cause: error });
    }
  }

  private waitForPlayableFrame(signal: AbortSignal): Promise<void> {
    const playable = (): boolean => this.video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA
      && this.video.videoWidth > 0 && this.video.videoHeight > 0;
    if (playable()) return Promise.resolve();
    return new Promise((resolve, reject) => {
      let timeout = 0;
      const cleanup = (): void => {
        window.clearTimeout(timeout);
        signal.removeEventListener('abort', onAbort);
        this.video.removeEventListener('loadeddata', onReady);
        this.video.removeEventListener('playing', onReady);
        this.video.removeEventListener('resize', onReady);
      };
      const onReady = (): void => {
        if (!playable()) return;
        cleanup();
        resolve();
      };
      const onAbort = (): void => {
        cleanup();
        reject(signal.reason ?? new DOMException('Camera start aborted.', 'AbortError'));
      };
      signal.addEventListener('abort', onAbort, { once: true });
      this.video.addEventListener('loadeddata', onReady);
      this.video.addEventListener('playing', onReady);
      this.video.addEventListener('resize', onReady);
      timeout = window.setTimeout(() => {
        cleanup();
        reject(new Error('Kamera tidak menampilkan gambar. Periksa kamera lalu coba lagi.'));
      }, 8000);
      onReady();
    });
  }

  stop(): void {
    this.stream?.getTracks().forEach((track) => {
      track.removeEventListener('ended', this.onEnded);
      track.stop();
    });
    this.stream = undefined;
    this.video.pause();
    this.video.srcObject = null;
    this.video.hidden = true;
  }
}
