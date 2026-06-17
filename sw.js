/* Sanctum of Ash — service worker.
   The game HTML is served NETWORK-FIRST so a fresh build is picked up immediately when online
   (it falls back to the cached copy offline). Small assets stay cache-first. Bump CACHE per release. */
const CACHE = 'sanctum-v14';
const ASSETS = [
  './sanctum-of-ash.html',
  './manifest.webmanifest',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const isDoc = req.mode === 'navigate' || req.destination === 'document' || /\.html(\?|$)/.test(req.url);
  if (isDoc) {
    // network-first: always try the latest build when online; fall back to cache offline
    e.respondWith(
      fetch(req).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy));
        return res;
      }).catch(() => caches.match(req).then(hit => hit || caches.match('./sanctum-of-ash.html')))
    );
    return;
  }
  // everything else (manifest, icons): cache-first
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(req, copy));
      return res;
    }).catch(() => caches.match('./sanctum-of-ash.html')))
  );
});
