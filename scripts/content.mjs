import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root=path.resolve(import.meta.dirname,'..');process.chdir(root);
const command=process.argv[2]||'validate';
const read=file=>JSON.parse(fs.readFileSync(file,'utf8'));
const hash=value=>crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');
const write=(file,value)=>{fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file+'.tmp',JSON.stringify(value,null,2)+'\n');fs.renameSync(file+'.tmp',file);};
const files=folder=>fs.existsSync(folder)?fs.readdirSync(folder).filter(f=>f.endsWith('.json')).sort():[];
const str=value=>typeof value==='string'&&value.trim().length>0;
const arr=value=>Array.isArray(value)&&value.every(str);
const iso=value=>typeof value==='string'&&Number.isFinite(Date.parse(value));
const args=Object.fromEntries(process.argv.slice(3).reduce((pairs,arg,i,list)=>arg.startsWith('--')?[...pairs,[arg.slice(2),list[i+1]]]:pairs,[]));
const sources=read('content/research/sources.json'),skills=read('content/research/skills.json');
const batches=files('content/batches').map(f=>({file:f,...read('content/batches/'+f)}));
if(command==='prepare'){
  const kind=args.kind==='questions'?'questions':'vocab',size=Number(args.count||(kind==='vocab'?100:30));
  if(!Number.isInteger(size)||size<1||size>100)throw Error('countは1〜100');
  const existing=[...batches.map(b=>b.id),...files('content/requests').map(f=>f.replace('.json',''))];
  let index=1;while(existing.includes(`${kind}-${String(index).padStart(3,'0')}`))index++;
  const id=`${kind}-${String(index).padStart(3,'0')}`,output=`content/batches/${id}.json`;
  const prompt=`docs/progress.md, docs/research.md, docs/content-contract.md, AGENTS.md を読んでください。${kind==='vocab'?'vocabulary_editor':'question_author'}へ委任し、${size}${kind==='vocab'?'見出し語':'問'}の独自教材を ${output} に作成してください。既存IDと重複させず、実在する出典・語義だけを参照。reviewStatusはpending。生成後 npm run content:blind を実行し、著者解答を読んでいない content_reviewer へ検証を委任してください。独立解答保存後に正解・解説と比較し、疑義は修正して版を上げ再検査。全項目を実際に検証したら npm run content:validate && npm run content:integrate && npm run build && npm test を実行してください。教材数・未完了・制約を報告してください。人手確認を偽らないでください。`;
  write(`content/requests/${id}.json`,{id,kind,size,createdAt:new Date().toISOString(),status:'awaiting-author',model:null,output,prompt});
  fs.writeFileSync(`content/requests/${id}.md`,`# ${id} 教材補充依頼\n\n${prompt}\n\nこのプロジェクトをCodexで開き「content/requests/${id}.md を実行してください」と依頼してください。通常学習にAI APIは不要です。この準備コマンド自体は教材を生成しません。\n`);
  console.log(`作業指示を作成: content/requests/${id}.md\n既存チェックポイント: content/checkpoint.json`);process.exit(0);
}
if(command==='blind'){
  let count=0;
  for(const batch of batches.filter(b=>b.id.startsWith('questions-'))){write(`content/blind/${batch.id}.json`,{id:batch.id,items:batch.items.map(({id,version,stem,options})=>({id,version,stem,options}))});count+=batch.items.length;}
  console.log(`${count}問を正解・解説なしで書き出しました。これだけを未閲覧の検証担当に渡してください。`);process.exit(0);
}
const reviewFiles=files('content/reviews').filter(f=>/-review(?:[^/]*)?\.json$/.test(f));
const reviewMap=new Map(),reviewRecords=[],errors=[],warnings=[];
for(const file of reviewFiles){
  const report=read('content/reviews/'+file);
  if(!Array.isArray(report.items)||!iso(report.createdAt)||!str(report.reviewer)||!str(report.method)||report.reviewerType!=='ai'){errors.push(`${file}: 内容検査の実施情報が不正`);continue;}
  for(const item of report.items){
    if(!str(item.targetId)||!Number.isInteger(item.targetVersion)||!['accepted','revise','rejected'].includes(item.decision)||!Array.isArray(item.issues)||!str(item.reason)){errors.push(`${file}: 検査項目が不正`);continue;}
    const record={...item,reviewerType:report.reviewerType,reviewer:report.reviewer,createdAt:report.createdAt,reviewId:report.id};
    const key=`${item.targetId}@${item.targetVersion}`;
    const previous=reviewMap.get(key);
    if(!previous||previous.createdAt<=record.createdAt)reviewMap.set(key,record);
    reviewRecords.push(record);
  }
}
const vocabulary=[],questions=[],ids=new Set(),lemmas=new Set(),senseIds=new Set(),sourceIds=new Set(sources.map(s=>s.id)),skillIds=new Set(skills.map(s=>s.id)),validIds=new Set();
for(const batch of batches){
  if(!str(batch.id)||batch.schemaVersion!==1||!iso(batch.createdAt)||!str(batch.author)||!str(batch.input)||!str(batch.status)||!Array.isArray(batch.items)){errors.push(`${batch.file}: バッチ形式が不正`);continue;}
  for(const item of batch.items){
    const start=errors.length;
    const fail=message=>errors.push(`${batch.id}/${item.id??'?'}: ${message}`);
    if(!str(item.id)||!Number.isInteger(item.version)||item.version<1)fail('ID/版');
    if(ids.has(item.id))fail('教材ID重複');ids.add(item.id);
    if(!['foundation','standard','stretch'].includes(item.difficulty))fail('仮難易度');
    if(!arr(item.sourceIds)||!item.sourceIds.length||!item.sourceIds.every(s=>sourceIds.has(s)))fail('出典参照');
    if(!['pending','accepted','revise','rejected'].includes(item.reviewStatus))fail('検査状態');
    if(batch.id.startsWith('vocab-')){
      vocabulary.push(item);
      if(!str(item.lemma)||!/^[a-z][a-z'-]*$/i.test(item.lemma))fail('見出し語（複数語は関連データへ）');
      const normalized=item.lemma?.toLowerCase();if(lemmas.has(normalized))fail('見出し語重複');lemmas.add(normalized);
      if(!['office','business','travel','daily','finance','people','technology','logistics','health','environment'].includes(item.domain))fail('語彙分野');
      if(!str(item.rationale)||!['design','official','research','learning-design'].includes(item.evidenceType)||!arr(item.relatedWords))fail('選定根拠/関連語');
      if(!Array.isArray(item.senses)||!item.senses.length)fail('語義');
      for(const sense of item.senses??[]){
        if(!['id','pos','meaningJa','example','translationJa'].every(k=>str(sense[k]))||!arr(sense.collocations)||!sense.collocations.length)fail('語義の不足');
        if(senseIds.has(sense.id))fail('語義ID重複');senseIds.add(sense.id);
      }
    }else if(batch.id.startsWith('questions-')){
      questions.push(item);
      if(item.type!=='part5'||!str(item.stem)||item.stem.split('_____').length!==2)fail('問題種別/空所');
      if(!Array.isArray(item.options)||item.options.length!==4||item.options.some(o=>!str(o.id)||!str(o.text))||new Set(item.options.map(o=>o.id)).size!==4||new Set(item.options.map(o=>o.text.toLowerCase())).size!==4)fail('四択');
      if(!item.options?.some(o=>o.id===item.answerId))fail('正解ID');
      if(!str(item.translationJa)||!str(item.explanationJa)||!item.optionExplanations||!item.options?.every(o=>str(item.optionExplanations[o.id])))fail('和訳/説明欠落');
      if(!skillIds.has(item.skillId)||!arr(item.secondarySkillIds)||!item.secondarySkillIds.every(s=>skillIds.has(s))||!str(item.familyId))fail('技能/ファミリー');
      if(!arr(item.vocabularySenseIds))fail('語義参照形式');
    }else fail('バッチ種別');
    if(errors.length===start)validIds.add(item.id);
  }
}
const stems=new Map(),positionCounts={},skillCounts={},familyCounts={};
for(const q of questions){
  if(!q.vocabularySenseIds?.every(id=>senseIds.has(id))){errors.push(`${q.id}: 未登録語義への参照`);validIds.delete(q.id);}
  const normalized=q.stem?.toLowerCase().replace(/[^a-z_ ]/g,'').replace(/\s+/g,' ');
  if(stems.has(normalized)){errors.push(`${q.id}: ${stems.get(normalized)}と同文`);validIds.delete(q.id);}stems.set(normalized,q.id);
  positionCounts[q.answerId]=(positionCounts[q.answerId]??0)+1;skillCounts[q.skillId]=(skillCounts[q.skillId]??0)+1;familyCounts[q.familyId]=(familyCounts[q.familyId]??0)+1;
  const review=reviewMap.get(`${q.id}@${q.version}`);
  if(review?.decision==='accepted'&&review.independentAnswerId!==q.answerId){errors.push(`${q.id}: 独立解答と著者の解答が不一致`);validIds.delete(q.id);}
}
const tokenSets=questions.map(q=>new Set(q.stem.toLowerCase().match(/[a-z]+/g)));
for(let i=0;i<questions.length;i++)for(let j=i+1;j<questions.length;j++){
  const a=tokenSets[i],b=tokenSets[j],union=new Set([...a,...b]);const similarity=[...a].filter(t=>b.has(t)).length/union.size;
  if(similarity>.72)warnings.push(`類似候補 ${questions[i].id}/${questions[j].id} (${Math.round(similarity*100)}%) family ${questions[i].familyId===questions[j].familyId?'共通':'要確認'}`);
}
if(questions.length&&Math.max(...Object.values(positionCounts))>questions.length*.4)warnings.push('正解位置が40%を超えて偏っています。');
for(const skill of skills)if(!(skillCounts[skill.id]>0))warnings.push(`技能${skill.id}が未収録`);
const accepted=item=>validIds.has(item.id)&&reviewMap.get(`${item.id}@${item.version}`)?.decision==='accepted';
const approvedVocab=vocabulary.filter(accepted),approvedSenseIds=new Set(approvedVocab.flatMap(v=>v.senses.map(s=>s.id)));
const approvedQuestions=questions.filter(q=>accepted(q)&&q.vocabularySenseIds.every(id=>approvedSenseIds.has(id)));
const human=fs.existsSync('content/human-reviews.json')?read('content/human-reviews.json'):[];
const countHuman=items=>items.filter(item=>human.some(r=>r.targetId===item.id&&r.targetVersion===item.version&&r.reviewerType==='human'&&r.decision==='accepted'&&iso(r.createdAt)&&str(r.reviewer))).length;
const metrics={target:{vocabulary:1000,questions:300},generated:{vocabulary:vocabulary.length,questions:questions.length},schemaPassed:{vocabulary:vocabulary.filter(v=>validIds.has(v.id)).length,questions:questions.filter(q=>validIds.has(q.id)).length},aiContentPassed:{vocabulary:vocabulary.filter(accepted).length,questions:questions.filter(accepted).length},humanReviewed:{vocabulary:countHuman(vocabulary),questions:countHuman(questions)},deliverable:{vocabulary:approvedVocab.length,questions:approvedQuestions.length},senseCount:approvedVocab.reduce((n,v)=>n+v.senses.length,0)};
const report={checkedAt:new Date().toISOString(),metrics,errors,warnings,positionCounts,skillCounts,familyCounts};
write('content/validation-report.json',report);
write('content/checkpoint.json',{schemaVersion:1,updatedAt:new Date().toISOString(),metrics,batches:batches.map(b=>({id:b.id,input:b.input,createdAt:b.createdAt,model:b.model??null,count:b.items?.length??0,status:b.items?.every(accepted)?'reviewed':'awaiting-review-or-revision',failedIds:b.items?.filter(i=>!accepted(i)).map(i=>i.id)??[]})),next:'npm run content:prepare -- --kind vocab|questions --count 100|30。既存の未検証バッチは新規生成せずcontent_reviewerへ委任。content/validation-report.jsonを確認。'});
if(errors.length){console.error(JSON.stringify({errors,metrics},null,2));process.exit(1);}
if(command==='integrate'){
  const invalidated=fs.existsSync('content/invalidated.json')?read('content/invalidated.json'):[];
  if(!Array.isArray(invalidated)||!invalidated.every(str))throw Error('invalidated形式不正');
  const vocabulary=approvedVocab.map(v=>({...v,reviewStatus:'accepted'})),questions=approvedQuestions.map(q=>({...q,reviewStatus:'accepted'}));
  const releasedIds=new Set([...vocabulary,...questions].map(i=>`${i.id}@${i.version}`));
  const reviews=[...reviewMap.values()].filter(r=>releasedIds.has(`${r.targetId}@${r.targetVersion}`));
  const payload={sources,skills,vocabulary,questions,reviews,invalidated};
  const version='1.'+hash(payload).slice(0,12);
  const previous=fs.existsSync('content/master.json')?read('content/master.json'):null;
  if(previous?.version!==version){
    if(previous)write(`content/archive/${previous.version}.json`,previous);
    write('content/master.json',{schemaVersion:1,version,generatedAt:new Date().toISOString(),...payload});
  }
  console.log(`検査済み教材を原子的に統合: ${vocabulary.length}語 / ${questions.length}問 / ${version}`);
}
if(command==='sample'){
  const lines=['# 教材の抜き取り確認一覧','',`生成日時: ${new Date().toISOString()}。人間確認未実施。以下は各バッチ冒頭の抜き取りです。全教材はcontent/batchesを参照。指摘はアプリの報告またはID/版付きで記録してください。`];
  for(const batch of batches){lines.push('',`## ${batch.id}`,'');for(const item of batch.items.slice(0,3)){lines.push(`### ${item.id} / v${item.version}`,'');if(item.lemma){lines.push(item.lemma);for(const s of item.senses)lines.push(`- ${s.pos}: ${s.meaningJa} — ${s.example} / ${s.translationJa}`);}else{lines.push(item.stem,'',...item.options.map(o=>`- ${o.id}: ${o.text}`),'',`正解: ${item.answerId}。${item.explanationJa}`,item.translationJa);}}}
  fs.writeFileSync('docs/content-sample.md',lines.join('\n')+'\n');console.log('docs/content-sample.md を生成');
}
const row=(label,key)=>`| ${label} | ${metrics[key].vocabulary} | ${metrics[key].questions} |`;
fs.writeFileSync('docs/content-quality.md',`# 教材品質レポート\n\n最終形式検査: ${report.checkedAt}\n\n|区分|見出し語|Part 5問題|\n|---|---:|---:|\n${row('目標','target')}\n${row('生成済み（重複除外）','generated')}\n${row('形式検査通過','schemaPassed')}\n${row('実施済みAI内容検査通過','aiContentPassed')}\n${row('人手確認','humanReviewed')}\n${row('配信可能（参照も検査済み）','deliverable')}\n\n配信可能語義 ${metrics.senseCount} 件。活用形やコロケーションを見出し語数に加算しません。\n\n## 検査の区別\n\n- 形式検査: ID/見出し語/英文重複、必須項目、4択、出典/語義/技能参照、説明欠落、正解位置、類似語集合をコードで検査。\n- 内容検査: content/reviews の実施記録のみ集計。問題文と選択肢だけから独立解答を保存してから著者解答・解説を比較。単語は意味/用例/和訳/語法を実際に読む。AI同士の一致は正しさの保証ではありません。\n- 人手確認: content/human-reviews.json の実施記録のみ。AIが人間確認を捏造しません。\n- 修正版には新しい版の検査が必要。未検証、要修正、不採用、参照先語義が未検証の問題は配信しません。\n- 主観的な難易度は未校正。公式問題ではなく、本試験の出題率、スコア換算や800点取得を保証しません。\n\n## 配分と注意点\n\n技能別: ${JSON.stringify(skillCounts)}\n\n正解位置: ${JSON.stringify(positionCounts)}\n\n類似検出・偏りの警告: ${warnings.length}件。${warnings.slice(0,30).join(' / ')||'現在なし。'}\n\n全件の失敗理由/警告は content/validation-report.json、バッチ状態は content/checkpoint.json、抜き取り確認は docs/content-sample.md を参照。生成数と配信数の差は未実施または修正待ちです。\n`);
console.log(JSON.stringify(metrics,null,2));
if(warnings.length)console.log(`注意 ${warnings.length}件: content/validation-report.json を確認`);
