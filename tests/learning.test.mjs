import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {emptyState,defaults,refKey,reviewKey} from '../dist/core/types.js';
import {ActiveClock,advance,createSession,due,eligibleAttempts,localDay,makePlan,recordAnswer,recordRecall,recommendation,saveSense,schedule,skillStats} from '../dist/core/learning.js';
import {unknownReferences,validateBackup,validateContent} from '../dist/core/validation.js';
const content=JSON.parse(fs.readFileSync(new URL('../content/master.json',import.meta.url)));
const when=new Date('2026-10-04T14:55:00Z');
function setup(){const s=emptyState();const session=createSession(s,content,'study',when,'session-test');s.sessions.push(session);return {s,session,q:content.questions.find(q=>q.id===session.items[0].targetId)};}
function backup(s){return {app:'step800',schemaVersion:1,exportedAt:when.toISOString(),contentVersion:content.version,state:s};}

test('配信教材は形式検査と対応する内容検査を通過している',()=>{
  const c=validateContent(content);assert.ok(c.vocabulary.length>=100);assert.ok(c.questions.length>=25);
  const broken=structuredClone(c);broken.questions[0].vocabularySenseIds=['unknown'];assert.throws(()=>validateContent(broken),/語義参照/);
  const pending=structuredClone(c);pending.questions[0].reviewStatus='pending';assert.throws(()=>validateContent(pending),/未検証/);
});
test('同じ回答は連打・再開しても1件で復習回数も増えない',()=>{
  const {s,session,q}=setup();const a=recordAnswer(s,content,session.id,0,q.answerId,'sure',12345,when);
  const resumed=structuredClone(s);const b=recordAnswer(resumed,content,session.id,0,q.options.find(o=>o.id!==q.answerId).id,'guess',99999,when);
  assert.deepEqual(a,b);assert.equal(resumed.attempts.length,1);assert.equal(resumed.reviews[reviewKey('question',q.id)].count,1);
  assert.equal(a.activeMs,12345);assert.equal(a.confidence,'sure');
});
test('未回答で進めず、回答後の中断位置と教材版を保持する',()=>{
  const {s,session,q}=setup();assert.throws(()=>advance(s,session.id,when),/先に回答/);
  recordAnswer(s,content,session.id,0,q.answerId,null,3000,when);advance(s,session.id,when);
  const restored=validateBackup(JSON.parse(JSON.stringify(backup(s)))).state;
  assert.equal(restored.sessions[0].cursor,1);assert.equal(restored.snapshots[refKey(q.id,q.version)].stem,q.stem);
});
test('初見と再挑戦・同じfamilyは別に集計し根拠数を水増ししない',()=>{
  const {s,session,q}=setup();recordAnswer(s,content,session.id,0,q.answerId,'sure',1000,when);
  const second={...structuredClone(session),id:'second',items:[session.items[0]],cursor:0};s.sessions.push(second);recordAnswer(s,content,'second',0,q.answerId,'sure',1000,when);
  const cousin={...q,id:'q-cousin'};const changed={...content,questions:[...content.questions,cousin]};
  s.sessions.push({...structuredClone(second),id:'third',items:[{...second.items[0],targetId:cousin.id}]});recordAnswer(s,changed,'third',0,cousin.answerId,null,1000,when);
  const stats=skillStats(s,changed).find(sk=>sk.id===q.skillId);assert.equal(stats.total,1);assert.equal(stats.repeatCount,2);assert.equal(stats.provisional,true);
  assert.deepEqual(s.attempts.map(a=>a.firstAttempt),[true,false,true]);
});
test('教材の無効化・版更新でも履歴と復習を残し、不良版を推薦から除外する',()=>{
  const {s,session,q}=setup();recordAnswer(s,content,session.id,0,q.options.find(o=>o.id!==q.answerId).id,null,1000,when);
  const changed={...content,questions:content.questions.map(x=>x.id===q.id?{...x,version:x.version+1}:x),invalidated:[refKey(q.id,q.version)]};
  assert.equal(eligibleAttempts(s,changed).length,0);assert.equal(s.attempts.length,1);assert.ok(s.reviews[reviewKey('question',q.id)]);assert.ok(s.snapshots[refKey(q.id,q.version)]);
  assert.equal(skillStats(s,changed).find(sk=>sk.id===q.skillId).total,0);
});
test('ユーザーが除外した版への将来の解答も統計から除外する',()=>{
  const {s,session,q}=setup();s.flags.push({id:'f',targetId:q.id,targetVersion:q.version,excludeFromStats:true,message:'曖昧',status:'open',createdAt:when.toISOString()});
  recordAnswer(s,content,session.id,0,q.answerId,null,1000,when);assert.equal(eligibleAttempts(s,content).length,0);assert.equal(s.attempts.length,1);
});
test('正答でも勘・迷いは短い復習間隔、忘却は最初に戻る',()=>{
  let r;for(let i=0;i<5;i++)r=schedule(r,'question','q',1,'remembered',defaults,when);
  assert.equal(r.stage,4);assert.equal((Date.parse(r.dueAt)-when.getTime())/86400000,30);
  const uncertain=schedule(r,'question','q',1,'unsure',defaults,when);assert.equal(uncertain.stage,1);assert.equal((Date.parse(uncertain.dueAt)-when.getTime())/86400000,3);
  const wrong=schedule(r,'question','q',1,'forgot',defaults,when);assert.equal(wrong.stage,0);
  const {s,session,q}=setup();recordAnswer(s,content,session.id,0,q.answerId,'guess',1000,when);assert.equal(s.reviews[reviewKey('question',q.id)].lastResult,'unsure');
});
test('東京の深夜をまたぐ復習と夏時間のある地域も利用者の日付で判定する',()=>{
  assert.equal(localDay('2026-10-04T15:01:00Z','Asia/Tokyo'),'2026-10-05');
  const r=schedule(undefined,'question','q',1,'forgot',defaults,new Date('2026-10-03T16:30:00Z'));
  assert.equal(due(r,new Date('2026-10-04T14:59:00Z'),'Asia/Tokyo'),false);
  assert.equal(due(r,new Date('2026-10-04T15:00:00Z'),'Asia/Tokyo'),true);
  assert.equal(localDay('2026-03-08T07:30:00Z','America/New_York'),'2026-03-08');
});
test('非表示・中断時間はActiveClockから除かれ、二重startでも増えない',()=>{
  let time=0;const clock=new ActiveClock(()=>time);clock.start();time=1250;clock.start();assert.equal(clock.drain(),1250);
  time=2250;clock.pause();time=999999;assert.equal(clock.drain(),1000);clock.start();time+=400;assert.equal(clock.drain(),400);assert.equal(clock.drain(),0);
});
test('語義別の保存・メモ・想起記録は別々、評価連打は予定を重複更新しない',()=>{
  const s=emptyState();const v=content.vocabulary.find(v=>v.senses.length>1);assert.ok(v);
  const [a,b]=v.senses;saveSense(s,content,a.id,when);saveSense(s,content,b.id,when);
  s.saved[a.id].note='場面と一緒に覚える';recordRecall(s,content,a.id,'remembered','event1','session',when);recordRecall(s,content,a.id,'forgot','event1','session',when);
  assert.equal(s.recalls.length,1);assert.equal(s.reviews[reviewKey('vocabulary',a.id)].count,1);assert.equal(s.reviews[reviewKey('vocabulary',b.id)].count,0);assert.equal(s.saved[a.id].note,'場面と一緒に覚える');
  assert.deepEqual(validateBackup(JSON.parse(JSON.stringify(backup(s)))).state,s);
});
test('出題は期限到来50%・重点30%・他分野20%、候補不足でも重複せず成立',()=>{
  const s=emptyState();for(const q of content.questions.slice(-6))s.reviews[reviewKey('question',q.id)]={id:reviewKey('question',q.id),kind:'question',targetId:q.id,targetVersion:q.version,dueAt:when.toISOString(),stage:0,lastResult:'forgot',count:1};
  const plan=makePlan(content,s,'study',when,10);assert.equal(plan.length,10);assert.equal(plan.slice(0,5).every(p=>p.mode==='review'),true);assert.equal(new Set(plan.map(p=>p.kind+p.targetId)).size,10);
  const tiny={...content,questions:[content.questions[0]],vocabulary:[]};assert.equal(makePlan(tiny,s,'study',when,10).length,1);assert.equal(makePlan({...tiny,questions:[]},s,'study',when,10).length,0);
  const newState=emptyState();assert.match(recommendation(newState,content).reason,/幅広く/);assert.ok(new Set(makePlan(content,newState,'study',when,10).map(p=>content.questions.find(q=>q.id===p.targetId).skillId)).size>=5);
});
test('全問学習済みの場合は新しい問題と偽らず再挑戦を表示',()=>{
  const {s,session,q}=setup();recordAnswer(s,content,session.id,0,q.answerId,null,1000,when);
  const tiny={...content,questions:[q],vocabulary:[]};assert.equal(makePlan(tiny,s,'study',when,10)[0].mode,'review');
});
test('初回チェックは6技能と3語義、スコア推定なしで完了・中断できる',()=>{
  const s=emptyState();const session=createSession(s,content,'check',when,'check');s.sessions.push(session);
  assert.equal(session.items.filter(i=>i.kind==='question').length,6);assert.equal(session.items.filter(i=>i.kind==='vocabulary').length,3);
  for(let i=0;i<session.items.length;i++){const item=session.items[i];if(item.kind==='question'){const q=content.questions.find(q=>q.id===item.targetId);recordAnswer(s,content,session.id,i,q.answerId,null,1000,when);}else recordRecall(s,content,item.targetId,'remembered',`${session.id}:${i}`,session.id,when);advance(s,session.id,when);}
  assert.equal(session.status,'complete');assert.equal(s.checkDone,true);assert.equal(s.settings.currentScore,520);
});
test('バックアップが破損・未知形式・重複・不正日付なら拒否する',()=>{
  const {s,session,q}=setup();recordAnswer(s,content,session.id,0,q.answerId,null,1000,when);
  const good=backup(s);for(const mutate of [b=>b.schemaVersion=2,b=>b.state.attempts.push(b.state.attempts[0]),b=>b.state.reviews[reviewKey('question',q.id)].dueAt='bad',b=>b.state.settings.timezone='not/a/timezone',b=>b.state.attempts[0].activeMs=-1,b=>b.state.attempts[0].correct=false,b=>delete b.state.snapshots[refKey(q.id,q.version)]]){const b=structuredClone(good);mutate(b);assert.throws(()=>validateBackup(b));}
  assert.equal(s.attempts.length,1);
});
test('現在の教材にないIDもスナップショットを保持し復元前に明示',()=>{
  const {s,session,q}=setup();recordAnswer(s,content,session.id,0,q.answerId,null,1000,when);
  const b=validateBackup(backup(s));const unknown=unknownReferences(b,{...content,questions:[]});assert.ok(unknown.includes(q.id));assert.equal(b.state.attempts.length,1);assert.ok(b.state.snapshots[refKey(q.id,q.version)]);
});
