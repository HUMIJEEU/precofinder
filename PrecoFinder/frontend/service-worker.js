self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('pf-cache-v1').then((cache) => cache.addAll([
      './',
      './index.html',
      './script.js',
      './manifest.webmanifest',
      './assets/icon.png'
    ]))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((resp) => resp || fetch(event.request))
  );
});