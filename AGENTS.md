# TOEIC 800 学習アプリ

まず docs/progress.md、docs/content-contract.md、docs/research.md を読む。
既存の学習履歴と教材版を破壊しない。教材作成とレビューは別担当へ委任する。
trend_researcher は調査ファイル、vocabulary_editor と question_author は自分のバッチ、content_reviewer はレビューのみ担当する。主担当が検査して統合する。
未実施の検査に合格印を付けない。問題の検証は正解を含まない content/blind から始め、独立解答を保存してから作成担当の解答を見る。
曖昧な教材は保留する。公式問題を転載しない。人間による確認をAIで代替したと表示しない。
実行: npm run typecheck / npm test / npm run content:validate / npm run build。
