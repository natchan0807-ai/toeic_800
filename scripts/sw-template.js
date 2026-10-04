const SCOPE = new URL(self.registration.scope);
const CACHE_PREFIX = 'step800-' + encodeURIComponent(SCOPE.href) + '-';
const CACHE = CACHE_PREFIX + '__CACHE_VERSION__';
const FILES = __PRECACHE_FILES__;
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(async cache => {
    try { await cache.addAll(FILES); } catch (error) { await caches.delete(CACHE); throw error; }
  }));
});
self.addEventListener('activate', event => {
  event.waitUntil((async()=>{
    await self.clients.claim();
    const keys=await caches.keys();
    await Promise.all(keys.filter(k=>k.startsWith(CACHE_PREFIX)&&k!==CACHE).map(k=>caches.delete(k)));
  })());
});
self.addEventListener('message', event => {
  if(event.data==='CACHE_STATUS') event.source?.postMessage({type:'CACHE_READY',cache:CACHE});
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if(event.request.method!=='GET'||url.origin!==SCOPE.origin||!url.pathname.startsWith(SCOPE.pathname))return;
  event.respondWith((async()=>{
    const cache=await caches.open(CACHE);
    const hit=await cache.match(event.request,{ignoreSearch:true});
    if(hit)return hit;
    if(event.request.mode==='navigate'&&(url.pathname===SCOPE.pathname||url.pathname===SCOPE.pathname+'index.html'))return await cache.match('./index.html')||fetch(event.request);
    return fetch(event.request);
  })());
});
