import '@fontsource/cormorant-garamond/latin-600.css';
import '@fontsource/plus-jakarta-sans/latin-400.css';
import '@fontsource/plus-jakarta-sans/latin-600.css';
import '@fontsource/plus-jakarta-sans/latin-700.css';
import { createProgressPacer } from './progressPacer';
import type { ProgressPacer } from './progressPacer';

type CacheManifest = {
  version: string;
  totalBytes: number;
  files: Array<{ url: string; size: number }>;
};

type QueueReply = { admitted: boolean; position: number; waiting: number };

const downloadScreen = document.querySelector<HTMLElement>('#download-screen');
const title = document.querySelector<HTMLElement>('#download-title');
const statusText = document.querySelector<HTMLElement>('#download-status');
const detail = document.querySelector<HTMLElement>('#download-detail');
const progress = document.querySelector<HTMLElement>('#download-progress');
const progressbar = document.querySelector<HTMLElement>('[role="progressbar"]');
const percent = document.querySelector<HTMLElement>('#download-percent');
const retry = document.querySelector<HTMLButtonElement>('#download-retry');

if (!downloadScreen || !title || !statusText || !detail || !progress || !progressbar || !percent || !retry) {
  throw new Error('Elemen layar unduhan tidak lengkap.');
}

const cachePrefix = 'wayang-app-';
const clientIdKey = 'wayang-queue-client';
const versionKey = 'wayang-cache-version';
const randomId = typeof crypto.randomUUID === 'function'
  ? crypto.randomUUID()
  : `${Date.now()}-${Math.random().toString(36).slice(2)}-${Math.random().toString(36).slice(2)}`;
const clientId = sessionStorage.getItem(clientIdKey) ?? randomId;
sessionStorage.setItem(clientIdKey, clientId);
let heartbeat: number | undefined;

const justDownloadedKey = 'wayang-just-downloaded';
let pacer: ProgressPacer | undefined;

/** Real progress goes through the pacer, which guarantees a visible 0→100% over at least 2 s. */
function setProgress(value: number): void {
  pacer?.set(value);
}

function renderProgress(value: number): void {
  const safeValue = Math.max(0, Math.min(100, Math.round(value)));
  progress!.style.width = `${safeValue}%`;
  progressbar!.setAttribute('aria-valuenow', String(safeValue));
  percent!.textContent = `${safeValue}%`;
}

async function queue(action: 'join' | 'status' | 'release'): Promise<QueueReply> {
  const response = await fetch(`/queue.php?action=${action}&client=${encodeURIComponent(clientId)}`, {
    cache: 'no-store',
  });
  if (!response.ok) throw new Error('Layanan antrean tidak tersedia.');
  return response.json() as Promise<QueueReply>;
}

async function waitForTurn(): Promise<void> {
  title!.textContent = 'Menunggu giliran';
  setProgress(0);
  let reply = await queue('join');
  while (!reply.admitted) {
    statusText!.textContent = `Posisi antrean Anda: ${reply.position}`;
    detail!.textContent = `${reply.waiting} pengunjung sedang menunggu. Antrean diproses sesuai urutan masuk.`;
    await new Promise((resolve) => window.setTimeout(resolve, 1500));
    reply = await queue('status');
  }
  heartbeat = window.setInterval(() => { void queue('status').catch(() => undefined); }, 15000);
}

async function hasCompleteCache(manifest: CacheManifest): Promise<boolean> {
  if (localStorage.getItem(versionKey) !== manifest.version) return false;
  const appCache = await caches.open(`${cachePrefix}${manifest.version}`);
  const matches = await Promise.all(manifest.files.map(({ url }) => appCache.match(url)));
  return matches.every(Boolean);
}

async function downloadApp(manifest: CacheManifest): Promise<void> {
  const cacheName = `${cachePrefix}${manifest.version}`;
  await caches.delete(cacheName);
  const appCache = await caches.open(cacheName);
  let downloaded = 0;
  let cursor = 0;

  const showDownloaded = (): void => {
    setProgress(manifest.totalBytes ? (downloaded / manifest.totalBytes) * 100 : 100);
  };

  title!.textContent = 'Mohon tunggu, sedang menyiapkan aset dan aplikasi';
  detail!.textContent = 'Mohon jangan tutup halaman ini.';
  statusText!.textContent = '';

  const worker = async (): Promise<void> => {
    while (cursor < manifest.files.length) {
      const file = manifest.files[cursor++];
      const response = await fetch(file.url, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Gagal mengunduh ${file.url}`);
      // Stream the body so the bar moves while large files (model, wasm, audio) download.
      const chunks: Uint8Array[] = [];
      let fileBytes = 0;
      const reader = response.body?.getReader();
      if (reader) {
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          chunks.push(value);
          const counted = Math.min(value.length, Math.max(0, file.size - fileBytes));
          fileBytes += value.length;
          downloaded += counted;
          showDownloaded();
        }
      }
      // Body is already decoded, so keep only the content type (never content-encoding/length).
      const body = reader ? new Blob(chunks as BlobPart[]) : await response.blob();
      await appCache.put(file.url, new Response(body, {
        headers: { 'Content-Type': response.headers.get('content-type') ?? 'application/octet-stream' },
      }));
      downloaded += Math.max(0, file.size - fileBytes);
      showDownloaded();
    }
  };

  await Promise.all([worker(), worker()]);
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames
    .filter((name) => name.startsWith(cachePrefix) && name !== cacheName)
    .map((name) => caches.delete(name)));
  localStorage.setItem(versionKey, manifest.version);
}

async function startApplication(paced = true): Promise<void> {
  await import('./main');
  setProgress(100);
  if (paced) await pacer?.finish();
  downloadScreen!.classList.add('is-hidden');
  window.setTimeout(() => downloadScreen!.remove(), 400);
}

async function boot(): Promise<void> {
  pacer?.cancel();
  pacer = createProgressPacer(renderProgress);
  retry!.hidden = true;
  title!.textContent = 'Mohon tunggu, sedang menyiapkan aset dan aplikasi';

  // Dev server has no build-time asset manifest; skip offline cache and queue.
  if (import.meta.env.DEV) {
    statusText!.textContent = 'Memuat aplikasi…';
    await startApplication();
    return;
  }

  // Right after a fresh download the bar already ran to 100%; open without a second run.
  if (sessionStorage.getItem(justDownloadedKey)) {
    sessionStorage.removeItem(justDownloadedKey);
    pacer.cancel();
    renderProgress(100);
    statusText!.textContent = 'Membuka Wayang Bali…';
    await startApplication(false);
    return;
  }

  statusText!.textContent = 'Memeriksa paket aplikasi…';
  detail!.textContent = 'Mohon jangan tutup halaman ini.';

  if (!('serviceWorker' in navigator) || !('caches' in window)) {
    throw new Error('Browser belum mendukung penyimpanan aplikasi. Gunakan Chrome, Edge, atau Safari terbaru.');
  }

  const registration = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
  await navigator.serviceWorker.ready;
  const manifestResponse = await fetch('/asset-manifest.json', { cache: 'no-store' });
  if (!manifestResponse.ok) throw new Error('Daftar paket aplikasi tidak dapat dimuat.');
  const manifest = await manifestResponse.json() as CacheManifest;

  if (await hasCompleteCache(manifest)) {
    registration.active?.postMessage({ type: 'USE_CACHE', version: manifest.version });
    statusText!.textContent = 'Memuat dari perangkat…';
    await startApplication();
    return;
  }

  await waitForTurn();
  try {
    await downloadApp(manifest);
  } finally {
    if (heartbeat !== undefined) window.clearInterval(heartbeat);
    await queue('release').catch(() => undefined);
  }

  registration.active?.postMessage({ type: 'USE_CACHE', version: manifest.version });
  setProgress(100);
  await pacer.finish();
  sessionStorage.setItem(justDownloadedKey, '1');
  title!.textContent = 'Unduhan selesai';
  statusText!.textContent = 'Membuka Wayang Bali…';
  detail!.textContent = 'Kunjungan berikutnya akan dimuat dari perangkat Anda.';
  window.setTimeout(() => window.location.reload(), 450);
}

void boot().catch((error: unknown) => {
  console.error(error);
  title!.textContent = 'Belum berhasil memuat';
  statusText!.textContent = error instanceof Error ? error.message : 'Terjadi kesalahan saat menyiapkan aplikasi.';
  detail!.textContent = 'Periksa koneksi internet, lalu coba lagi.';
  retry!.hidden = false;
});

retry.addEventListener('click', () => { void boot(); });
