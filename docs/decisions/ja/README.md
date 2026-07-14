# 決定記録

このディレクトリは、個々のチャットセッションや実装のターンを超えて生き残るべきプロジェクト決定を記録します。

## コンテンツ

- **0000-hierarchical_csv_binding_spec.md**- 階層CSV結合モデルの作業ノート。
- **0001-workspace-scope.md**- リポジトリの境界を定義し、実行時間依存ではなく、外部XBRL-GLワークスペースを参照として扱います。
- **0002-en16931-first-openpeppol-overlay.md**- 後にオーバーレイとして最初の変換ベースラインとOpenPeppolとしてEN 16931を確立します。
- **0003-lhm-level-effective-hierarchy.md**- 構造化されたCSVおよびタクソノミ生成によって使用される有効な階層として**lhm level**を記述して下さい。
- **0004-xbrl-csv-only-taxonomy.md**- Phase 1 タクソノミ 出力をxBRL-CSVに制限し、タクソノミのエントリーポイントとして**en16931-oim**とtuple/contentスキーマはありません。
- **0005-xbrl-csv-metadata-and-roundtrip-validation.md**- xBRL-CSVメタデータJSONおよびスキーマ検証済みの往復XMLの使用に関する文書。
- **0006-local-taxonomy-generator.md**- UADC - 互換性のあるタクソノミジェネレータがこのリポジトリに保存されているレコード。
- **0007-binding-tables-are-runtime-authority.md**- 運用コンバータがバインディング表sを使用し、ランタイムLHMのフォールバックではなく、ソース列を決定し、行スコープを繰り返すレコード。
- **0008-xml-parent-context-recursion.md**- Phase 1転送変換モデルを録画し、XMLの親コンテキストを結合から再帰的に移動します**C**行。
- **0009-phase-output-naming-and-target-layout.md**- レコードPhase 1とPhase 2出力ディレクトリとファイル名の慣行。
- **0010-documentation-consolidation.md**- 現在のレコード 文書
スクリプトディレクトリ内の短いREADMEファイルで、5つのチャプター番号付きガイドに統合されます。

設計選択がデータモデル、タクソノミ形状、検証アプローチ、リポジトリ境界、または将来のフェーズプランを変更すると、新しい番号付き決定レコードを追加します。
