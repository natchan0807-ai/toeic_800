import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const code=fs.readFileSync(new URL('../dist/sw.js',import.meta.url),'utf8');
function harness(fail=false){
  const handlers={},cacheData=new Map([['step800-old',new Map([['./index.html','previous working app']])]]);let fetched=0;
  const self={location:{origin:'https://app.test'},addEventListener:(kind,handler)=>handlers[kind]=handler,clients:{claim:async()=>{}}};
  const caches={keys:async()=>[...cacheData.keys()],delete:async name=>cacheData.delete(name),open:async name=>{if(!cacheData.has(name))cacheData.set(name,new Map());const entries=cacheData.get(name);return {addAll:async files=>{for(const f of files){if(fail&&f.endsWith('content.json'))throw Error('network failure');entries.set(f,'cached '+f);}},match:async request=>{const key=typeof request==='string'?request:'./'+new URL(request.url).pathname.slice(1);return entries.get(key);}};}};
  vm.runInNewContext(code,{self,caches,URL,fetch:async()=>{fetched++;throw Error('offline');}});
  return {handlers,cacheData,get fetched(){return fetched;}};
}
test('教材保存後はオフラインでアプリと教材を取得できる（SW模擬環境）',async()=>{
  const h=harness();let pending;h.handlers.install({waitUntil:p=>pending=p});await pending;
  for(const path of ['/app.js','/data/content.json','/styles.css']){h.handlers.fetch({request:{method:'GET',url:'https://app.test'+path,mode:'cors'},respondWith:p=>pending=p});assert.match(await pending,/cached/);}
  h.handlers.fetch({request:{method:'GET',url:'https://app.test/',mode:'navigate'},respondWith:p=>pending=p});assert.match(await pending,/index.html/);assert.equal(h.fetched,0);
});
test('更新途中で取得失敗しても、使えていた旧キャッシュを削除しない',async()=>{
  const h=harness(true);let pending;h.handlers.install({waitUntil:p=>pending=p});await assert.rejects(pending,/network failure/);assert.equal(h.cacheData.size,1);assert.ok(h.cacheData.has('step800-old'));
});
test('キャッシュは配信アプリの全JS・CSS・教材を含む',()=>{
  const paths=fs.readdirSync(new URL('../dist',import.meta.url),{recursive:true}).filter(f=>f.endsWith('.js')||f.endsWith('.css')||f==='data/content.json');
  for(const p of paths.filter(p=>p!=='sw.js'))assert.ok(code.includes('./'+p),p);
});
