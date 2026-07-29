// ============================================================================
// 次元旅店 Service Worker
//
// 构建时由 scripts/stamp-sw.mjs 把 20260729102843 替换为构建版本号，
// 缓存名随之变为 inn-v<版本>。activate 时删除所有旧的 inn- 前缀缓存，
// 整体换新，防止旧版本锁死。
//
// 缓存策略：
//   - 页面导航（navigate / index.html） network-first，断网回退缓存
//   - assets/（hash 不可变）            cache-first
//   - cards/ audio/ scenes/（命名资源）  cache-first，换代随缓存名整体失效
//   - 其余（跨域 / 非 GET / 目录外请求）  一律放行
// ============================================================================

const VERSION = '20260729102843'
const CACHE_PREFIX = 'inn-'
const CACHE = CACHE_PREFIX + 'v' + VERSION
// 游戏目录（SW scope 路径），根部署为 /，子路径部署为 /xxx/inn/
const BASE = new URL(self.registration.scope).pathname
const INDEX_URL = new URL('index.html', self.registration.scope).href
const MANIFEST_URL = new URL('sw-manifest.json', self.registration.scope).href

// ---------- install：读取构建清单，预载并广播进度 ----------
self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const res = await fetch(MANIFEST_URL, { cache: 'no-cache' })
      if (!res.ok) throw new Error('[inn-sw] 无法读取 sw-manifest.json：HTTP ' + res.status)
      const manifest = await res.json()
      const list = Array.isArray(manifest.precache) ? manifest.precache : []
      const total = list.length
      const cache = await caches.open(CACHE)
      let done = 0

      const broadcast = async (payload) => {
        const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true })
        for (const client of clients) client.postMessage(payload)
      }

      // 6 路并发拉取，每完成一项汇报一次进度；
      // 任何一项失败则 install 整体失败，下次进入自动重试，不会写入半个缓存。
      const queue = list.slice()
      await Promise.all(
        Array.from({ length: 6 }, async () => {
          while (queue.length > 0) {
            const item = queue.shift()
            const url = new URL(item, self.registration.scope).href
            const resp = await fetch(url, { cache: 'no-cache' })
            if (!resp.ok) throw new Error('[inn-sw] 预载失败：' + item + '（HTTP ' + resp.status + '）')
            await cache.put(url, resp)
            done += 1
            await broadcast({ type: 'progress', done, total })
          }
        })
      )

      await broadcast({ type: 'installed', version: VERSION, total })
      await self.skipWaiting()
    })()
  )
})

// ---------- activate：删除旧版本缓存，立即接管页面 ----------
self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const names = await caches.keys()
      await Promise.all(
        names
          .filter((name) => name.startsWith(CACHE_PREFIX) && name !== CACHE)
          .map((name) => caches.delete(name))
      )
      await self.clients.claim()
    })()
  )
})

// ---------- fetch：同源 GET 分流 ----------
self.addEventListener('fetch', (event) => {
  const req = event.request
  if (req.method !== 'GET') return
  const url = new URL(req.url)
  if (url.origin !== self.location.origin) return

  // 页面导航：network-first
  if (req.mode === 'navigate') {
    event.respondWith(networkFirst(req))
    return
  }

  // 只接管游戏目录内的资源，目录外一律放行
  if (!url.pathname.startsWith(BASE)) return
  const rel = url.pathname.slice(BASE.length)
  if (
    rel.startsWith('assets/') ||
    rel.startsWith('cards/') ||
    rel.startsWith('audio/') ||
    rel.startsWith('scenes/')
  ) {
    event.respondWith(cacheFirst(req))
  }
  // sw.js / sw-manifest.json / _redirects 等其余文件：不拦截，走浏览器默认
})

// 导航：优先网络（no-cache 强制向源站再验证，304 时开销极小），失败回退缓存
async function networkFirst(req) {
  const cache = await caches.open(CACHE)
  try {
    const fresh = await fetch(req, { cache: 'no-cache' })
    if (fresh.ok) cache.put(req, fresh.clone())
    return fresh
  } catch (err) {
    const cached = (await caches.match(req)) || (await caches.match(INDEX_URL))
    if (cached) return cached
    throw err
  }
}

// 静态资源：先查缓存，未命中则联网拉取并写入缓存。
// 注意：统一按完整 URL 拉取（不带 Range），因为 Cache API 无法存储 206 部分内容；
// 对媒体 range 请求返回 200 全量是合法响应，浏览器可正常播放。
async function cacheFirst(req) {
  const cached = await caches.match(req.url)
  if (cached) return cached
  const fresh = await fetch(req.url, { cache: 'no-cache' })
  if (fresh.status === 200) {
    const cache = await caches.open(CACHE)
    cache.put(req.url, fresh.clone())
  }
  return fresh
}
