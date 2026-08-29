[English](../semantic_binding.md) | **日本語**

# semantic_binding

## 目的

`src/semantic_binding.py` は規定上の双方向 Semantic Binding runtime です。明示された Semantic Binding Table に従い Structured CSV ⇄ Structured CSV の mapping を行います。

存在しない `semantic_table.py` 契約は規定 program ではありません。

## 入力

- source Structured CSV
- source / target HMD
- Semantic Binding CSV
- taxonomy extension overlay と QName map
- target OIM taxonomy entry point

## CLI

```text
py src/semantic_binding.py <input.csv> --binding <binding.csv> --source-hmd <source.csv> --target-hmd <target.csv> --overlay <overlay.csv> --qname-map <qname-map.csv> --output <output.csv> --taxonomy <entrypoint.xsd>
```

## 規則

mapping は `semantic_path` で明示し、local-name 又は QName の類似性から推測しません。selector 条件は独立した selector 列ではなく `semantic_path` に記述します。binding で定義された equality、presence、`not(presence)` predicate を扱います。

variant 選択は同一 canonical Class occurrence 内の supplementary semantic fact に基づきます。source / target syntax 名から直接選択してはなりません。現行 Formal GIT には standalone `oim_metadata.py` は存在しません。OIM metadata 生成は既存 runtime 実装内に残っており、本書は metadata 処理が独立した common module に抽出済みとは記載しません。

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
