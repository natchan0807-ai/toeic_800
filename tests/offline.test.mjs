import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const code=fs.readFileSync(new URL('../dist/sw.js',import.meta.url),'utf8');
function harness(fail=false,scope='https://app.test/',cacheData=new Map([['step800-old',new Map([['./index.html','previous working app']])]])){
  const handlers={};let fetched=0;
  const self={registration:{scope},addEventListener:(kind,handler)=>handlers[kind]=handler,clients:{claim:async()=>{}}};
  const caches={keys:async()=>[...cacheData.keys()],delete:async name=>cacheData.delete(name),open:async name=>{if(!cacheData.has(name))cacheData.set(name,new Map());const entries=cacheData.get(name);return {addAll:async files=>{for(const f of files){if(fail&&f.endsWith('content.json'))throw Error('network failure');entries.set(new URL(f,scope).href,'cached '+f);}},match:async request=>{const url=new URL(typeof request==='string'?request:request.url,scope);url.search='';return entries.get(url.href);}};}};
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
test('本番と開発版の更新は互いのオフライン用キャッシュを削除しない',async()=>{
  const shared=new Map(),production=harness(false,'https://app.test/toeic_800/',shared),preview=harness(false,'https://app.test/toeic_800/develop/',shared);
  let pending;
  for(const h of [production,preview]){h.handlers.install({waitUntil:p=>pending=p});await pending;}
  const installed=[...shared.keys()];assert.equal(installed.length,2);
  const old='step800-'+encodeURIComponent('https://app.test/toeic_800/develop/')+'-old';shared.set(old,new Map());
  for(const h of [preview,production]){h.handlers.activate({waitUntil:p=>pending=p});await pending;}
  assert.deepEqual([...shared.keys()],installed);assert.equal(shared.has(old),false);
  for(const [h,path] of [[production,'/toeic_800/'],[preview,'/toeic_800/develop/']]){
    h.handlers.fetch({request:{method:'GET',url:'https://app.test'+path,mode:'navigate'},respondWith:p=>pending=p});
    assert.match(await pending,/index.html/);assert.equal(h.fetched,0);
  }
});
test('本番のService Workerは開発URLに本番の画面を返さない',async()=>{
  const h=harness(false,'https://app.test/toeic_800/');let pending;
  h.handlers.install({waitUntil:p=>pending=p});await pending;
  h.handlers.fetch({request:{method:'GET',url:'https://app.test/toeic_800/develop/',mode:'navigate'},respondWith:p=>pending=p});
  await assert.rejects(pending,/offline/);assert.equal(h.fetched,1);
});
test('開発版のService Workerは本番URLを処理しない',()=>{
  const h=harness(false,'https://app.test/toeic_800/develop/');let handled=false;
  h.handlers.fetch({request:{method:'GET',url:'https://app.test/toeic_800/',mode:'navigate'},respondWith:()=>handled=true});
  assert.equal(handled,false);assert.equal(h.fetched,0);
});
