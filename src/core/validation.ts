import type { Backup, Content, Question, UserState, Vocabulary } from './types.js';

function object(value:unknown):value is Record<string,unknown> {return !!value&&typeof value==='object'&&!Array.isArray(value);}
function text(value:unknown):value is string{return typeof value==='string'&&value.trim().length>0;}
function list(value:unknown):value is unknown[]{return Array.isArray(value);}
function number(value:unknown):value is number{return typeof value==='number'&&Number.isFinite(value)&&value>=0;}
function date(value:unknown):boolean{return typeof value==='string'&&/^\d{4}-\d{2}-\d{2}T/.test(value)&&Number.isFinite(Date.parse(value));}
function unique(values:unknown[],name:string):void {if(new Set(values).size!==values.length)throw Error(`${name}に重複があります。`);}
function assert(test:unknown,message:string):asserts test {if(!test)throw Error(message);}
function validQuestion(q:unknown):q is Question {
  return object(q)&&text(q.id)&&Number.isInteger(q.version)&&number(q.version)&&q.version>0&&q.type==='part5'&&text(q.stem)&&q.stem.includes('_____')&&list(q.options)&&q.options.length===4&&q.options.every(o=>object(o)&&text(o.id)&&text(o.text))&&new Set(q.options.map(o=>(o as {id:string}).id)).size===4&&q.options.some(o=>(o as {id:string}).id===q.answerId)&&text(q.translationJa)&&text(q.explanationJa)&&object(q.optionExplanations)&&q.options.every(o=>text((q.optionExplanations as Record<string,unknown>)[(o as {id:string}).id]))&&text(q.skillId)&&text(q.familyId)&&list(q.secondarySkillIds)&&q.secondarySkillIds.every(text)&&list(q.vocabularySenseIds)&&q.vocabularySenseIds.every(text)&&list(q.sourceIds)&&q.sourceIds.every(text)&&['foundation','standard','stretch'].includes(String(q.difficulty))&&text(q.reviewStatus);
}
function validVocabulary(v:unknown):v is Vocabulary {
  return object(v)&&text(v.id)&&Number.isInteger(v.version)&&number(v.version)&&v.version>0&&text(v.lemma)&&text(v.domain)&&text(v.rationale)&&text(v.evidenceType)&&text(v.reviewStatus)&&list(v.sourceIds)&&v.sourceIds.every(text)&&list(v.relatedWords)&&v.relatedWords.every(text)&&['foundation','standard','stretch'].includes(String(v.difficulty))&&list(v.senses)&&v.senses.length>0&&v.senses.every(s=>object(s)&&text(s.id)&&text(s.pos)&&text(s.meaningJa)&&text(s.example)&&text(s.translationJa)&&list(s.collocations)&&s.collocations.length>0&&s.collocations.every(text));
}
export function validateContent(input:unknown):Content {
  assert(object(input)&&input.schemaVersion===1&&text(input.version)&&date(input.generatedAt),'教材の形式・バージョンが不正です。');
  assert(list(input.questions)&&input.questions.every(validQuestion),'問題データに不足があります。');
  assert(list(input.vocabulary)&&input.vocabulary.every(validVocabulary),'単語データに不足があります。');
  assert(list(input.skills)&&input.skills.every(s=>object(s)&&text(s.id)&&text(s.name)&&text(s.description)&&text(s.parent)),'技能データが不正です。');
  assert(list(input.sources)&&input.sources.every(s=>object(s)&&text(s.id)&&text(s.url)&&/^https:\/\//.test(s.url)&&text(s.title)),'出典データが不正です。');
  assert(list(input.invalidated)&&input.invalidated.every(text),'無効版のリストが不正です。');
  assert(list(input.reviews),'教材の検査記録がありません。');
  const c=input as unknown as Content;
  unique(c.questions.map(q=>q.id),'問題ID');unique(c.vocabulary.map(v=>v.id),'語彙ID');unique(c.vocabulary.map(v=>v.lemma.toLowerCase()),'見出し語');unique(c.vocabulary.flatMap(v=>v.senses.map(s=>s.id)),'語義ID');
  unique(c.skills.map(s=>s.id),'技能ID');unique(c.sources.map(s=>s.id),'出典ID');
  const skills=new Set(c.skills.map(s=>s.id)), sources=new Set(c.sources.map(s=>s.id)), senses=new Set(c.vocabulary.flatMap(v=>v.senses.map(s=>s.id)));
  for(const item of [...c.questions,...c.vocabulary]) {
    assert(item.reviewStatus==='accepted',`未検証教材です: ${item.id}`);
    assert(item.sourceIds.length&&item.sourceIds.every(id=>sources.has(id)),`出典参照が不正: ${item.id}`);
    assert(c.reviews.some(r=>r.targetId===item.id&&r.targetVersion===item.version&&r.decision==='accepted'),`内容検査記録が不足: ${item.id}`);
  }
  for(const q of c.questions){assert(skills.has(q.skillId)&&q.secondarySkillIds.every(id=>skills.has(id)),`技能参照が不正: ${q.id}`);assert(q.vocabularySenseIds.every(id=>senses.has(id)),`語義参照が不正: ${q.id}`);}
  return c;
}
export function validateBackup(input:unknown):Backup {
  assert(object(input)&&input.app==='step800'&&input.schemaVersion===1&&date(input.exportedAt)&&text(input.contentVersion),'このアプリのv1バックアップではありません。');
  const s=input.state;
  assert(object(s)&&s.schemaVersion===1&&typeof s.checkDone==='boolean','学習データの形式が不正です。');
  const cfg=s.settings;
  assert(object(cfg)&&number(cfg.targetScore)&&cfg.targetScore>=10&&cfg.targetScore<=990&&number(cfg.currentScore)&&cfg.currentScore<=990&&number(cfg.sessionMinutes)&&cfg.sessionMinutes>=1&&cfg.sessionMinutes<=60&&text(cfg.timezone)&&number(cfg.evidenceThreshold)&&cfg.evidenceThreshold>=1&&list(cfg.reviewIntervals)&&cfg.reviewIntervals.length>0&&cfg.reviewIntervals.every(n=>number(n)&&n>=1&&n<=365)&&number(cfg.reviewRatio)&&number(cfg.weakRatio)&&cfg.reviewRatio+cfg.weakRatio<=1,'設定の値が不正です。');
  try {new Intl.DateTimeFormat('en',{timeZone:cfg.timezone});}catch{throw Error('タイムゾーンが不正です。');}
  assert(list(s.attempts)&&list(s.sessions)&&list(s.flags)&&list(s.recalls)&&object(s.reviews)&&object(s.saved)&&object(s.snapshots),'履歴テーブルが不足しています。');
  const confidence=[null,'sure','unsure','guess'],recall=['remembered','unsure','forgot'];
  for(const a of s.attempts)assert(object(a)&&text(a.id)&&text(a.questionId)&&number(a.questionVersion)&&text(a.familyId)&&text(a.skillId)&&text(a.optionId)&&typeof a.correct==='boolean'&&number(a.activeMs)&&confidence.includes(a.confidence as string|null)&&typeof a.firstAttempt==='boolean'&&typeof a.excluded==='boolean'&&date(a.createdAt)&&text(a.sessionId)&&(a.reason===null||typeof a.reason==='string'),'解答履歴が不正です。');
  for(const session of s.sessions){
    assert(object(session)&&text(session.id)&&['study','check','review'].includes(String(session.mode))&&['active','paused','complete'].includes(String(session.status))&&list(session.items)&&number(session.cursor)&&Number.isInteger(session.cursor)&&session.cursor<=session.items.length&&number(session.activeMs)&&number(session.itemActiveMs)&&date(session.createdAt)&&date(session.updatedAt),'セッションが不正です。');
    for(const item of session.items)assert(object(item)&&['question','vocabulary'].includes(String(item.kind))&&text(item.targetId)&&number(item.version)&&['new','review','check'].includes(String(item.mode))&&text(item.reason),'出題順データが不正です。');
  }
  for(const [key,r] of Object.entries(s.reviews))assert(object(r)&&text(r.id)&&key===r.id&&['question','vocabulary'].includes(String(r.kind))&&text(r.targetId)&&number(r.targetVersion)&&date(r.dueAt)&&number(r.stage)&&Number.isInteger(r.stage)&&r.stage<cfg.reviewIntervals.length&&recall.includes(String(r.lastResult))&&number(r.count),'復習予定が不正です。');
  for(const [key,v] of Object.entries(s.saved))assert(object(v)&&key===v.id&&text(v.vocabularyId)&&number(v.vocabularyVersion)&&date(v.savedAt)&&typeof v.note==='string'&&list(v.encounteredQuestionIds)&&v.encounteredQuestionIds.every(text),'保存した単語のデータが不正です。');
  for(const f of s.flags)assert(object(f)&&text(f.id)&&text(f.targetId)&&number(f.targetVersion)&&text(f.message)&&['open','resolved'].includes(String(f.status))&&date(f.createdAt),'教材報告が不正です。');
  for(const r of s.recalls)assert(object(r)&&text(r.id)&&text(r.targetId)&&typeof r.sessionId==='string'&&recall.includes(String(r.result))&&date(r.createdAt),'語彙評価の履歴が不正です。');
  for(const [key,value] of Object.entries(s.snapshots))assert((validQuestion(value)||validVocabulary(value))&&key===`${value.id}@${value.version}`,'保存された教材版が不正です。');
  const state=s as unknown as UserState;
  unique(state.attempts.map(a=>a.id),'解答');unique(state.sessions.map(s=>s.id),'セッション');unique(state.flags.map(f=>f.id),'報告');unique(state.recalls.map(r=>r.id),'語彙評価');
  for(const a of state.attempts){const q=state.snapshots[`${a.questionId}@${a.questionVersion}`] as Question|undefined;assert(q?.type==='part5'&&q.options.some(o=>o.id===a.optionId)&&a.correct===(q.answerId===a.optionId),'解答と教材版の対応が不正です。');}
  for(const saved of Object.values(state.saved)){const v=state.snapshots[`${saved.vocabularyId}@${saved.vocabularyVersion}`] as Vocabulary|undefined;assert(v?.senses.some(s=>s.id===saved.id),'語義と保存教材版の対応が不正です。');}
  return input as unknown as Backup;
}
export function unknownReferences(backup:Backup,content:Content):string[] {
  const ids=new Set([...content.questions.map(q=>q.id),...content.vocabulary.flatMap(v=>v.senses.map(s=>s.id))]);
  return [...new Set([...backup.state.attempts.map(a=>a.questionId),...Object.keys(backup.state.saved),...backup.state.sessions.flatMap(s=>s.items.map(i=>i.targetId))])].filter(id=>!ids.has(id));
}
