import { type Attempt,type Confidence,type Content,type PlanItem,type Question,type Recall,type ReviewState,type Settings,type StudySession,type UserState,reviewKey,refKey } from './types.js';

export function localDay(iso:string|Date,timezone:string):string {
  const parts = new Intl.DateTimeFormat('en-CA',{timeZone:timezone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date(iso));
  return ['year','month','day'].map(key=>parts.find(p=>p.type===key)!.value).join('-');
}
export function due(review:ReviewState,now:Date,timezone:string):boolean {return localDay(review.dueAt,timezone)<=localDay(now,timezone);}
export function schedule(previous:ReviewState|undefined,kind:'question'|'vocabulary',targetId:string,version:number,result:Recall,settings:Settings,now:Date):ReviewState {
  const stage=result==='forgot'?0:result==='unsure'?Math.min(previous?.stage??0,1):Math.min(previous?previous.stage+1:0,settings.reviewIntervals.length-1);
  return {id:reviewKey(kind,targetId),kind,targetId,targetVersion:version,stage,dueAt:new Date(now.getTime()+(settings.reviewIntervals[stage]??1)*86400000).toISOString(),lastResult:result,count:(previous?.count??0)+1};
}
export function eligibleAttempts(state:UserState,content:Content):Attempt[] {
  return state.attempts.filter(a=>!a.excluded&&!content.invalidated.includes(refKey(a.questionId,a.questionVersion))&&!state.flags.some(f=>f.excludeFromStats&&f.targetId===a.questionId&&f.targetVersion===a.questionVersion));
}
export function skillStats(state:UserState,content:Content) {
  const attempts=eligibleAttempts(state,content);
  const seen=new Set<string>();
  const independent=attempts.filter(a=>{if(seen.has(a.familyId))return false;seen.add(a.familyId);return true;});
  return content.skills.map(skill=>{
    const list=independent.filter(a=>a.skillId===skill.id);
    const all=attempts.filter(a=>a.skillId===skill.id);
    const correct=list.filter(a=>a.correct).length;
    const unsure=list.filter(a=>a.confidence==='guess'||a.confidence==='unsure').length;
    return {...skill,total:list.length,correct,rate:list.length?correct/list.length:null,unsure,guesses:list.filter(a=>a.confidence==='guess').length,averageMs:list.length?list.reduce((n,a)=>n+a.activeMs,0)/list.length:0,repeatCount:all.length-list.length,repeatCorrect:all.filter(a=>!list.includes(a)&&a.correct).length,provisional:list.length<state.settings.evidenceThreshold,priority:list.length?((list.length-correct)+unsure*.35)/(list.length+3):0};
  });
}
export function recommendation(state:UserState,content:Content):{skillId:string;name:string;reason:string} {
  const stats=skillStats(state,content);
  const sparse=stats.filter(s=>s.total<3).sort((a,b)=>a.total-b.total)[0];
  if(sparse)return {skillId:sparse.id,name:sparse.name,reason:`${sparse.name}の記録は${sparse.total}問。まず幅広く確認しましょう。`};
  const weakest=[...stats].sort((a,b)=>b.priority-a.priority)[0];
  if(!weakest)return {skillId:'pos',name:'品詞',reason:'いろいろな分野を少しずつ確認しましょう。'};
  return {skillId:weakest.id,name:weakest.name,reason:`${weakest.name}で${weakest.total}問中${weakest.total-weakest.correct}問の誤答、${weakest.unsure}問で迷いがありました。${weakest.provisional?'まだ参考値です。':'新しい問題で確かめましょう。'}`};
}
export function findQuestion(content:Content,state:UserState,id:string,version?:number):Question|undefined {
  const q=content.questions.find(q=>q.id===id&&(version===undefined||q.version===version));
  return q??(version===undefined?undefined:state.snapshots[refKey(id,version)] as Question|undefined);
}
export function makePlan(content:Content,state:UserState,mode:StudySession['mode'],now:Date,limit=10):PlanItem[] {
  const questions=content.questions.filter(q=>q.reviewStatus==='accepted'&&!content.invalidated.includes(refKey(q.id,q.version)));
  const seenIds=new Set(state.attempts.map(a=>a.questionId));
  const seenFamilies=new Set(eligibleAttempts(state,content).map(a=>a.familyId));
  const items:PlanItem[]=[];
  const used=new Set<string>();
  const families=new Set<string>();
  const add=(item:PlanItem)=>{const key=item.kind+item.targetId;if(used.has(key)||items.length>=limit)return false;used.add(key);items.push(item);if(item.kind==='question'){const q=questions.find(q=>q.id===item.targetId);if(q)families.add(q.familyId);}return true;};
  const qItem=(q:Question,mode:PlanItem['mode'],reason:string):PlanItem=>({kind:'question',targetId:q.id,version:q.version,mode,reason});
  if(mode==='check') {
    for(const skill of content.skills.slice(0,6)){const q=questions.find(q=>q.skillId===skill.id&&!seenIds.has(q.id));if(q)add(qItem(q,'check','初回チェック・スコア診断ではありません'));}
    for(const v of content.vocabulary.slice(0,3))if(v.senses[0])add({kind:'vocabulary',targetId:v.senses[0].id,version:v.version,mode:'check',reason:'意味を思い出して確認'});
    return items;
  }
  const dueItems=Object.values(state.reviews).filter(r=>due(r,now,state.settings.timezone)).sort((a,b)=>a.dueAt.localeCompare(b.dueAt));
  const usableDue:PlanItem[]=[];
  for(const r of dueItems){
    if(r.kind==='question'){const q=questions.find(q=>q.id===r.targetId);if(q)usableDue.push(qItem(q,'review','復習予定日になった問題です'));}
    else {const v=content.vocabulary.find(v=>v.senses.some(s=>s.id===r.targetId));if(v&&state.saved[r.targetId])usableDue.push({kind:'vocabulary',targetId:r.targetId,version:v.version,mode:'review',reason:'保存した語義の復習'});}
  }
  if(mode==='review'){usableDue.slice(0,limit).forEach(add);return items;}
  usableDue.slice(0,Math.round(limit*state.settings.reviewRatio)).forEach(add);
  const rec=recommendation(state,content);
  const fresh=questions.filter(q=>!seenIds.has(q.id)&&!seenFamilies.has(q.familyId));
  let weak=0;
  for(const q of fresh.filter(q=>q.skillId===rec.skillId))if(!families.has(q.familyId)&&weak<Math.round(limit*state.settings.weakRatio)){if(add(qItem(q,'new',rec.reason)))weak++;}
  // Round-robin ensures sparse learners see a broad set of skills.
  const skillOrder=[...content.skills].sort((a,b)=>(skillStats(state,content).find(s=>s.id===a.id)?.total??0)-(skillStats(state,content).find(s=>s.id===b.id)?.total??0));
  for(let round=0;round<limit;round++)for(const s of skillOrder){const q=fresh.find(q=>q.skillId===s.id&&!used.has('question'+q.id)&&!families.has(q.familyId));if(q)add(qItem(q,'new','別の分野もバランスよく確認'));}
  usableDue.forEach(add);
  for(const q of questions)if(!used.has('question'+q.id))add(qItem(q,'review',seenIds.has(q.id)?'学習済みの問題をもう一度':'同じ型を学習済みの類題です'));
  return items;
}
export function createSession(state:UserState,content:Content,mode:StudySession['mode'],now:Date,id:string):StudySession {
  const timings=eligibleAttempts(state,content).slice(-20).map(a=>a.activeMs).filter(n=>n>1000);
  const mean=timings.length?timings.reduce((a,b)=>a+b,0)/timings.length:25000;
  const limit=Math.max(3,Math.min(12,Math.floor(state.settings.sessionMinutes*60000/(mean+35000))));
  return {id,mode,items:makePlan(content,state,mode,now,mode==='check'?9:limit),cursor:0,status:'active',createdAt:now.toISOString(),updatedAt:now.toISOString(),activeMs:0,itemActiveMs:0};
}
export function recordAnswer(state:UserState,content:Content,sessionId:string,index:number,optionId:string,confidence:Confidence,activeMs:number,now:Date):Attempt {
  const session=state.sessions.find(s=>s.id===sessionId);
  if(!session||session.cursor!==index)throw Error('セッション位置が変わりました。再読み込みしてください。');
  const id=`${sessionId}:${index}`;
  const existing=state.attempts.find(a=>a.id===id);if(existing)return existing;
  const item=session.items[index];if(!item||item.kind!=='question')throw Error('問題が見つかりません。');
  const q=findQuestion(content,state,item.targetId,item.version);
  if(!q||!q.options.some(o=>o.id===optionId))throw Error('選択肢が見つかりません。');
  const correct=optionId===q.answerId;
  const attempt:Attempt={id,questionId:q.id,questionVersion:q.version,familyId:q.familyId,skillId:q.skillId,optionId,correct,confidence,activeMs:Math.max(0,Math.round(activeMs)),firstAttempt:!state.attempts.some(a=>a.questionId===q.id),reason:null,createdAt:now.toISOString(),sessionId,excluded:content.invalidated.includes(refKey(q.id,q.version))};
  state.attempts.push(attempt);state.snapshots[refKey(q.id,q.version)]=q;
  const result:Recall=!correct?'forgot':confidence==='guess'||confidence==='unsure'?'unsure':'remembered';
  state.reviews[reviewKey('question',q.id)]=schedule(state.reviews[reviewKey('question',q.id)],'question',q.id,q.version,result,state.settings,now);
  session.updatedAt=now.toISOString();return attempt;
}
export function saveSense(state:UserState,content:Content,senseId:string,now:Date,questionId?:string):void {
  const vocabulary=content.vocabulary.find(v=>v.senses.some(s=>s.id===senseId));
  if(!vocabulary)throw Error('この語義は現在の教材にありません。');
  const old=state.saved[senseId];
  state.saved[senseId]={id:senseId,vocabularyId:vocabulary.id,vocabularyVersion:vocabulary.version,savedAt:old?.savedAt??now.toISOString(),note:old?.note??'',encounteredQuestionIds:[...new Set([...(old?.encounteredQuestionIds??[]),...(questionId?[questionId]:[])])]};
  state.snapshots[refKey(vocabulary.id,vocabulary.version)]=vocabulary;
  const key=reviewKey('vocabulary',senseId);
  if(!state.reviews[key])state.reviews[key]={id:key,kind:'vocabulary',targetId:senseId,targetVersion:vocabulary.version,dueAt:now.toISOString(),stage:0,lastResult:'forgot',count:0};
}
export function recordRecall(state:UserState,content:Content,senseId:string,result:Recall,eventId:string,sessionId:string,now:Date):void {
  if(state.recalls.some(r=>r.id===eventId))return;
  saveSense(state,content,senseId,now);
  const v=content.vocabulary.find(v=>v.senses.some(s=>s.id===senseId))!;
  const key=reviewKey('vocabulary',senseId);
  const previous=state.reviews[key];
  state.reviews[key]=schedule(previous?.count?previous:undefined,'vocabulary',senseId,v.version,result,state.settings,now);
  state.recalls.push({id:eventId,targetId:senseId,sessionId,result,createdAt:now.toISOString()});
}
export function advance(state:UserState,sessionId:string,now:Date):void {
  const s=state.sessions.find(s=>s.id===sessionId);if(!s)return;
  const item=s.items[s.cursor];
  const answered=item?.kind==='question'?state.attempts.some(a=>a.id===`${s.id}:${s.cursor}`):state.recalls.some(r=>r.id===`${s.id}:${s.cursor}`);
  if(!answered)throw Error('先に回答してください。');
  s.cursor++;s.itemActiveMs=0;s.updatedAt=now.toISOString();
  if(s.cursor>=s.items.length){s.status='complete';if(s.mode==='check')state.checkDone=true;}
}
export class ActiveClock {
  private since:number|null=null;
  private elapsed=0;
  constructor(private readonly now:()=>number=()=>performance.now()){}
  start(){if(this.since===null)this.since=this.now();}
  pause(){if(this.since!==null){this.elapsed+=Math.max(0,this.now()-this.since);this.since=null;}}
  drain(){const running=this.since!==null;this.pause();const result=this.elapsed;this.elapsed=0;if(running)this.start();return result;}
}
