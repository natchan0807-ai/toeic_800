import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as types from '../dist/core/types.js';
import * as learning from '../dist/core/learning.js';
import * as html from '../dist/ui/html.js';

const content=JSON.parse(fs.readFileSync(new URL('../content/master.json',import.meta.url)));
// Exercise the built app's rendering and click handler with a small DOM/storage harness.
// This checks the answer flow, not browser layout or native IndexedDB behavior.
const code=fs.readFileSync(new URL('../dist/app.js',import.meta.url),'utf8')
  .replace(/^import .*;\r?\n/gm,'')
  .replace('void boot();','globalThis.mount=(storage,material,id)=>{store=storage;content=material;sessionId=id;page="session";render();};');

function harness(){
  const initial=types.emptyState(),session=learning.createSession(initial,content,'study',new Date(),'answer-flow');
  session.items=content.questions.slice(0,2).map(q=>({kind:'question',targetId:q.id,version:q.version,mode:'new',reason:'テスト'}));
  initial.sessions.push(session);
  let failNext=false;
  const store={state:initial,async mutate(fn){
    await Promise.resolve();
    if(failNext){failNext=false;throw Error('保存できませんでした');}
    const next=structuredClone(this.state);fn(next);this.state=next;
  }};
  const app={innerHTML:''},toast={},answer={focus(options){this.focused=options;},scrollIntoView(options){this.scrolled=options;}};
  const listeners={};
  const document={hidden:true,addEventListener(name,handler){listeners[name]=handler;},querySelector(selector){
    if(selector==='#app')return app;
    if(selector==='#toast')return toast;
    if(selector==='.explanation'&&app.innerHTML.includes('class="panel explanation"'))return answer;
    return null;
  }};
  const context=vm.createContext({...types,...learning,...html,document,navigator:{onLine:true},window:{addEventListener(){},scrollTo(){}},setTimeout(){},Date,Error,structuredClone});
  vm.runInContext(code,context);context.mount(store,content,session.id);
  return {store,app,toast,answer,q:content.questions[0],failOnce(){failNext=true;},click(action,id=''){
    const target={dataset:{action,id},hasAttribute(){return false;}};
    return listeners.click({target:{closest(){return target;}}});
  }};
}

test('選択肢を押すだけで回答を保存し、正解・解説にフォーカスして即時移動する',async()=>{
  const h=harness();
  assert.doesNotMatch(h.app.innerHTML,/data-action="answer"|回答する/);
  await h.click('select',h.q.answerId);
  assert.equal(h.store.state.attempts.length,1);
  assert.equal(h.store.state.attempts[0].correct,true);
  assert.equal(h.store.state.sessions[0].cursor,0);
  assert.match(h.app.innerHTML,/正解です！/);
  assert.match(h.app.innerHTML,/class="panel explanation" tabindex="-1"/);
  assert.equal((h.app.innerHTML.match(/data-action="select"[^>]*disabled/g)||[]).length,4);
  assert.equal(h.answer.focused.preventScroll,true);
  assert.equal(h.answer.scrolled.behavior,'instant');
  assert.equal(h.answer.scrolled.block,'start');
});

test('誤答にもすぐ解説を表示し、次へ進むと未回答状態に戻る',async()=>{
  const h=harness(),wrong=h.q.options.find(o=>o.id!==h.q.answerId).id;
  await h.click('confidence','unsure');
  await h.click('select',wrong);
  assert.equal(h.store.state.attempts[0].correct,false);
  assert.equal(h.store.state.attempts[0].confidence,'unsure');
  assert.match(h.app.innerHTML,/あなたの回答/);
  assert.match(h.app.innerHTML,/ここで、理由を確認しましょう。/);
  await h.click('next');
  assert.equal(h.store.state.sessions[0].cursor,1);
  assert.doesNotMatch(h.app.innerHTML,/class="panel explanation"|data-action="answer"/);
  await h.click('select',content.questions[1].answerId);
  assert.equal(h.store.state.attempts.length,2);
  assert.equal(h.store.state.attempts[1].confidence,null);
});

test('選択肢を連打しても最初の回答と復習予定を1回だけ保存する',async()=>{
  const h=harness(),wrong=h.q.options.find(o=>o.id!==h.q.answerId).id;
  await Promise.all([h.click('select',h.q.answerId),h.click('select',wrong)]);
  await h.click('select',wrong);
  assert.equal(h.store.state.attempts.length,1);
  assert.equal(h.store.state.attempts[0].optionId,h.q.answerId);
  assert.equal(h.store.state.reviews[types.reviewKey('question',h.q.id)].count,1);
});

test('回答保存に失敗した場合は解説へ進まず、再選択で保存できる',async()=>{
  const h=harness();h.failOnce();
  await h.click('select',h.q.answerId);
  assert.equal(h.store.state.attempts.length,0);
  assert.doesNotMatch(h.app.innerHTML,/class="panel explanation"/);
  assert.match(h.toast.textContent,/保存できませんでした/);
  await h.click('select',h.q.answerId);
  assert.equal(h.store.state.attempts.length,1);
  assert.match(h.app.innerHTML,/正解です！/);
});
