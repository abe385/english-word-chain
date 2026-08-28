// 脳トレ(連想ゲーム)用のシンプルな Service Worker
// PWAとして「ホーム画面に追加」を可能にするために必要な最小限の実装。
// 高度なオフラインキャッシュ等は行わず、通常通りネットワークから読み込む。

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // 通常通りネットワークにそのまま流す(キャッシュ加工はしない)
  event.respondWith(fetch(event.request));
});
