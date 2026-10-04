const CACHE = 'step800-__CACHE_VERSION__';
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
    await Promise.all(keys.filter(k=>k.startsWith('step800-')&&k!==CACHE).map(k=>caches.delete(k)));
  })());
});
self.addEventListener('message', event => {
  if(event.data==='CACHE_STATUS') event.source?.postMessage({type:'CACHE_READY',cache:CACHE});
});
self.addEventListener('fetch', event => {
  if(event.request.method!=='GET'||new URL(event.request.url).origin!==self.location.origin)return;
  event.respondWith((async()=>{
    const cache=await caches.open(CACHE);
    const hit=await cache.match(event.request,{ignoreSearch:true});
    if(hit)return hit;
    if(event.request.mode==='navigate')return await cache.match('./index.html')||fetch(event.request);
    return fetch(event.request);
  })());
});
