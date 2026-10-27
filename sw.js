// Service Worker for K-12 Knowledge Graph PWA
const CACHE_NAME = 'k12-taxonomy-v6';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './diagnose/index.html',
  './explore/index.html',
  './children/index.html',
  './children/history.html',
  './children/children.css',
  './assets/children.js',
  './assets/site.css',
  './assets/home.js',
  './explore/app.js',
  './data/stats.json',
  './data/subjects.json',
  './manifest.webmanifest'
];

// Install event - cache core assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS_TO_CACHE))
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Clone and cache successful responses
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Fallback to cache on network failure
        return caches.match(event.request);
      })
  );
});
