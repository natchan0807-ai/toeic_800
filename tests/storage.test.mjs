import test from 'node:test';
import assert from 'node:assert/strict';
import {Store} from '../dist/core/storage.js';

// Transactional repository harness. Browser IndexedDB itself still needs the manual device checks.
function databaseHarness(){
  const tables={state:new Map(),content:new Map()};let queued=Promise.resolve();let failNext=false;
  return {tables,failOnce(){failNext=true;},transaction(name,mode){
    const tx={error:null,oncomplete:null,onabort:null,aborted:false,abort(){this.aborted=true;},objectStore(){return {get(key){const req={onsuccess:null,onerror:null,result:undefined};queued=queued.then(()=>new Promise(resolve=>setImmediate(()=>{const draft=new Map([...tables[name]].map(([k,v])=>[k,structuredClone(v)]));tx.draft=draft;req.result=structuredClone(draft.get(key));req.onsuccess?.();if(failNext){failNext=false;tx.error=Error('容量不足');tx.aborted=true;}if(tx.aborted)tx.onabort?.();else{tables[name]=draft;tx.oncomplete?.();}resolve();})));return req;},put(value,key){if(!tx.draft)throw Error('Harness expects a read before write');tx.draft.set(key,structuredClone(value));}};}};
    return tx;
  }};
}
test('連続書き込みは直前の保存状態を読み、再読み込み後も残る',async()=>{
  const db=databaseHarness(),store=new Store(db);
  await Promise.all([store.mutate(s=>s.settings.targetScore=850),store.mutate(s=>s.checkDone=true)]);
  const reload=new Store(db);await reload.load();assert.equal(reload.state.settings.targetScore,850);assert.equal(reload.state.checkDone,true);
});
test('別インスタンスからの更新を失わず、DB状態を毎回読む',async()=>{
  const db=databaseHarness(),a=new Store(db),b=new Store(db);
  await a.mutate(s=>s.settings.targetScore=875);await b.mutate(s=>s.checkDone=true);await a.load();assert.equal(a.state.settings.targetScore,875);assert.equal(a.state.checkDone,true);
});
test('保存に失敗すると現在の状態を変更せず、次の保存は再実行できる',async()=>{
  const db=databaseHarness(),store=new Store(db);await store.mutate(s=>s.checkDone=true);
  db.failOnce();await assert.rejects(store.mutate(s=>s.settings.targetScore=990),/容量不足/);assert.equal(store.state.settings.targetScore,800);
  await store.mutate(s=>s.settings.targetScore=850);assert.equal(store.state.settings.targetScore,850);
});
test('不正バックアップはトランザクション前に拒否し既存データを守る',async()=>{
  const db=databaseHarness(),store=new Store(db);await store.mutate(s=>s.checkDone=true);
  await assert.rejects(store.restore({app:'step800',schemaVersion:99}));await store.load();assert.equal(store.state.checkDone,true);
});
test('正常バックアップは設定と保存状態を原子的に復元する',async()=>{
  const db=databaseHarness(),store=new Store(db);await store.mutate(s=>{s.settings.targetScore=900;s.checkDone=true;});
  const backup=await store.backup('v1');await store.mutate(s=>{s.settings.targetScore=800;s.checkDone=false;});await store.restore(backup);
  assert.equal(store.state.settings.targetScore,900);assert.equal(store.state.checkDone,true);
});
