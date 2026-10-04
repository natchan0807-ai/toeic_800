# 教材契約 v1

教材はすべて独自生成。単語と問題の執筆担当は自分のバッチのみ編集する。レビュー前の状態は `pending`。検査履歴なしに合格へ変更しない。

## ファイル

`content/batches/vocab-001.json`（100語ずつ10バッチ）と `questions-001.json`（30問ずつ10バッチ）。トップレベルは `{ "id": "vocab-001", "schemaVersion": 1, "createdAt": "ISO UTC", "author": "vocabulary_editor", "model": null, "input": "research policy v1", "status": "generated", "items": [...] }`。

## 語彙

`{id:"v-approve",version:1,lemma:"approve",domain:"office",difficulty:"foundation",relatedWords:["approval"],rationale:"学習設計上の選定: 業務での承認",evidenceType:"design",sourceIds:["iibc-format"],reviewStatus:"pending",senses:[{id:"v-approve-1",pos:"verb",meaningJa:"承認する",example:"The manager approved our travel request.",translationJa:"部長は私たちの出張申請を承認しました。",collocations:["approve a request"]}]}`

- difficulty: foundation / standard / stretch（未校正）。domain: office / business / travel / daily / finance / people / technology / logistics / health / environment。
- 各見出し語に最低1語義。IDはASCII slugで安定化。活用形・派生語の大量追加で件数を増やさない。異なる用法のある基本語は同じ見出し語に別語義を設ける。

## 問題

`{id:"q-0001",version:1,type:"part5",stem:"The manager _____ the request yesterday.",options:[{id:"a",text:"approved"},{id:"b",text:"approving"},{id:"c",text:"approval"},{id:"d",text:"approves"}],answerId:"a",translationJa:"部長は昨日、その申請を承認しました。",explanationJa:"yesterdayが示す過去の動作なので過去形が必要です。",optionExplanations:{a:"approvedは過去形で文脈に合います。",b:"approvingだけでは述語になりません。",c:"approvalは名詞です。",d:"approvesは現在形です。"},skillId:"verb",secondarySkillIds:[],vocabularySenseIds:["v-approve-1"],difficulty:"foundation",familyId:"past-yesterday",sourceIds:["iibc-format"],reviewStatus:"pending"}`

- 正解位置を均等に。skillId: pos, verb, agreement, pronoun, preposition, conjunction, relative, comparison, determiner, vocabulary。
- 1バッチ30問、各技能3問。全体各技能30問。少数のテンプレートを語句だけ変えて増殖しない。類題は同じfamilyId。
- vocabularySenseIdsは実在語義のみ。初期語彙ができるまでは空配列で生成可能だが、統合までに実在語義と英文中の語を照合して関連付ける。

## 内容レビュー

`content/reviews/<batch>-review.json`: `{id,batchId,reviewerType:"ai",reviewer:"content_reviewer",createdAt,method,items:[{targetId,targetVersion:1,decision:"accepted"|"revise"|"rejected",independentAnswerId?:"a",issues:[],reason:"具体的な確認内容"}]}`。

問題の盲検入力は `content/blind/` に id,version,stem,options のみ出す。検証担当は著者解答を見る前に独立解答を `content/reviews/*-blind.json` へ保存。その後比較・解説検査。人間確認は別ファイルにのみ記録。
