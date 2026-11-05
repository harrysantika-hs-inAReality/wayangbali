const CACHE_PREFIX = 'wayang-app-';

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
      if (cached) return cached;
    }
    return fetch(request);
  })());
});
