// Service Worker for LinkedIn Studio & Dossier Career Radar (Offline-First PWA)
const CACHE_NAME = 'studio-cache-v3';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './dossier.html',
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
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW v2] Pre-caching static assets for offline mode...');
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn('[SW v2] Cache addAll warning:', err);
      });
    })
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

  // Network-First for HTML pages so user always sees the freshest updates immediately
  if (event.request.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname === '/' || url.pathname.endsWith('/dossier')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => {
          // If offline, fall back to cached version or appropriate fallback HTML
          return caches.match(event.request).then((cached) => {
            if (cached) return cached;
            if (url.pathname.includes('dossier')) {
              return caches.match('./dossier.html');
            }
            return caches.match('./index.html');
          });
        })
    );
    return;
  }

  // Cache-First for static assets (css, js, fonts, images)
  if (url.origin === location.origin && (url.pathname.includes('/assets/') || url.pathname.endsWith('.json') || url.pathname.endsWith('.svg'))) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        if (cached) return cached;
        return fetch(event.request).then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // Default: Network with cache fallback
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then((cached) => {
          if (cached) return cached;
          return new Response(JSON.stringify({ offline: true, error: 'Offline mode active' }), {
            headers: { 'Content-Type': 'application/json' }
          });
        });
      })
  );
});
