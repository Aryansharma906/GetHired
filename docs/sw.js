// Service Worker for LinkedIn Studio & Dossier Career Radar (Offline-First PWA)
const CACHE_NAME = 'studio-cache-v1';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  './assets/bootstrap.min.css',
  './assets/bootstrap.bundle.min.js',
  './assets/bootstrap-icons.min.css',
  './assets/fonts/bootstrap-icons.woff2',
  './assets/fonts/bootstrap-icons.woff',
  './assets/jszip.min.js',
  './assets/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Pre-caching static assets for offline mode...');
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn('[SW] Cache addAll warning:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Allow non-GET requests to pass through
  if (event.request.method !== 'GET') {
    return;
  }

  // Cache-first for local static assets
  if (url.origin === location.origin && (url.pathname.includes('/assets/') || url.pathname.endsWith('.html') || url.pathname.endsWith('.json') || url.pathname.endsWith('.svg'))) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        return cached || fetch(event.request).then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        });
      }).catch(() => caches.match('./index.html'))
    );
    return;
  }

  // Network-first with cache fallback for everything else
  event.respondWith(
    fetch(event.request).then((response) => {
      if (response && response.status === 200) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
      }
      return response;
    }).catch(() => {
      return caches.match(event.request).then((cached) => {
        if (cached) return cached;
        if (event.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
        return new Response(JSON.stringify({ offline: true, error: 'Offline mode active' }), {
          headers: { 'Content-Type': 'application/json' }
        });
      });
    })
  );
});
