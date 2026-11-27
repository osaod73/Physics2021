/* ===== رقم إصدار التطبيق: غيّره عند كل تحديث لـ index.html أو data.json ===== */
const VERSION = '1.0.0';

const SHELL = `pp-shell-${VERSION}`;   // الصفحة والبيانات (تُحدَّث مع كل إصدار)
const IMGS  = 'pp-img-v1';             // الصور (ثابتة؛ غيّر v1 إلى v2 إذا استبدلت صوراً بنفس أسمائها)

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(SHELL)
      .then(c => Promise.all(['./', 'index.html', 'data.json'].map(u => c.add(new Request(u, { cache: 'reload' })).catch(() => {}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k.startsWith('pp-shell-') && k !== SHELL).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', e => { if (e.data === 'SKIP_WAITING') self.skipWaiting(); });

self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin || u.pathname.endsWith('/sw.js')) return;

  // الصور: من الكاش أولاً ثم الشبكة (تعمل بدون إنترنت بعد أول تحميل)
  if (/\.(jpe?g|png)$/i.test(u.pathname)) {
    e.respondWith(caches.open(IMGS).then(async c => {
      const hit = await c.match(r);
      if (hit) return hit;
      const net = await fetch(r);
      if (net.ok) c.put(r, net.clone()).catch(() => {});
      return net;
    }));
    return;
  }

  // الصفحة وdata.json: من الشبكة أولاً (أحدث نسخة)، وعند انقطاع الإنترنت من الكاش
  e.respondWith(
    fetch(r, { cache: 'no-store' })
      .then(net => {
        if (net.ok) { const cp = net.clone(); caches.open(SHELL).then(c => c.put(new Request(u.origin + u.pathname), cp)); }
        return net;
      })
      .catch(() => caches.match(r, { ignoreSearch: true }).then(h => h || caches.match('index.html')))
  );
});
