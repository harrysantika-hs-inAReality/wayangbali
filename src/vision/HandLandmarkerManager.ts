import { FilesetResolver, HandLandmarker } from '@mediapipe/tasks-vision';
import type { HandLandmarkerResult } from '@mediapipe/tasks-vision';

export class HandLandmarkerManager {
  private constructor(private readonly landmarker: HandLandmarker) {}

  /** onModelProgress receives 0..1 while the model downloads (streamed when the size is known). */
  static async create(signal: AbortSignal, onModelProgress?: (fraction: number) => void): Promise<HandLandmarkerManager> {
    const base = import.meta.env.BASE_URL;
    let model: Uint8Array;
    try {
      const response = await fetch(`${base}models/hand_landmarker.task`, { signal });
      if (!response.ok || response.headers.get('content-type')?.includes('text/html')) {
        throw new Error('Model file was not found.');
      }
      model = await readWithProgress(response, onModelProgress);
      if (!model.length) throw new Error('Model file is empty.');
    } catch (error) {
      signal.throwIfAborted();
      throw new Error('Model pelacak tangan gagal dimuat. Periksa koneksi lalu coba lagi.', { cause: error });
    }

    try {
      const files = await FilesetResolver.forVisionTasks(`${base}mediapipe/wasm`);
      signal.throwIfAborted();
      const landmarker = await HandLandmarker.createFromOptions(files, {
        baseOptions: { modelAssetBuffer: model },
        runningMode: 'VIDEO',
        numHands: 2,
        minHandDetectionConfidence: 0.4,
        minHandPresenceConfidence: 0.4,
        minTrackingConfidence: 0.5,
      });
      if (signal.aborted) {
        landmarker.close();
        signal.throwIfAborted();
      }
      return new HandLandmarkerManager(landmarker);
    } catch (error) {
      signal.throwIfAborted();
      throw new Error('Pelacak tangan gagal disiapkan. Muat ulang halaman lalu coba lagi.', { cause: error });
    }
  }

  detect(video: HTMLVideoElement, timestamp: number): HandLandmarkerResult {
    return this.landmarker.detectForVideo(video, timestamp);
  }

  destroy(): void {
    this.landmarker.close();
  }
}

async function readWithProgress(response: Response, onProgress?: (fraction: number) => void): Promise<Uint8Array> {
  const total = Number(response.headers.get('content-length'));
  if (!onProgress || !response.body || !total) {
    const bytes = new Uint8Array(await response.arrayBuffer());
    onProgress?.(1);
    return bytes;
  }
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let received = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    received += value.length;
    onProgress(Math.min(1, received / total));
  }
  const bytes = new Uint8Array(received);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  onProgress(1);
  return bytes;
}
