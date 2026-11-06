const CACHE_PREFIX = 'wayang-app-';

async function cachedRangeResponse(request, cached) {
  const range = request.headers.get('range');
  if (!range || cached.status !== 200) return cached;
  const match = /^bytes=(\d*)-(\d*)$/.exec(range);
  // Let the server handle unsupported range formats and conditional requests.
  if (!match || (!match[1] && !match[2]) || request.headers.has('if-range')) return fetch(request);
  const body = await cached.blob();
  const size = body.size;
  const start = match[1] ? Number(match[1]) : Math.max(0, size - Number(match[2]));
  const end = match[1] && match[2] ? Math.min(Number(match[2]), size - 1) : size - 1;
  if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start > end || start >= size) {
    return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${size}` } });
  }
  const headers = new Headers(cached.headers);
  headers.delete('content-encoding');
  headers.set('Accept-Ranges', 'bytes');
  headers.set('Content-Range', `bytes ${start}-${end}/${size}`);
  headers.set('Content-Length', String(end - start + 1));
  return new Response(body.slice(start, end + 1), { status: 206, headers });
}

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => event.waitUntil(self.clients.claim()));

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin || request.mode === 'navigate') return;
  if (url.pathname === '/tutor.php' || url.pathname === '/queue.php' || url.pathname === '/asset-manifest.json' || url.pathname === '/sw.js') return;

  event.respondWith((async () => {
    const cacheNames = (await caches.keys()).filter((name) => name.startsWith(CACHE_PREFIX)).reverse();
    for (const cacheName of cacheNames) {
      const cached = await caches.match(request, { cacheName });
      if (cached) return cachedRangeResponse(request, cached);
    }
    return fetch(request);
  })());
});
