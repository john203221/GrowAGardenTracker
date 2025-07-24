// static/service-worker.js
self.addEventListener('install', event => {
  console.log('[SW] Installed');
});

self.addEventListener('activate', event => {
  console.log('[SW] Activated');
});

// You can expand this with fetch handlers if you want offline caching, etc.
