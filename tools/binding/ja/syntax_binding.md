[English](../syntax_binding.md) | **日本語**

# syntax_binding

## 目的

`src/syntax_binding.py` は、1つの semantic model について Syntax Binding CSV に従い XML ⇄ Structured CSV 変換を行います。

## 入力

- input XML or Structured CSV with `--reverse`
- Syntax Binding CSV
- Canonical HMD where required

## 出力

- Structured CSV plus OIM metadata JSON, or reconstructed XML

## CLI

```text
py src/syntax_binding.py <input> -b <binding.csv> -o <output> [--hmd-file <hmd.csv>] [--metadata-output <metadata.json>] [--taxonomy-base <dir>] [--reverse]
```

## OIM metadata

現行 Formal GIT には standalone `oim_metadata.py` は存在しません。OIM metadata 生成は既存 runtime 実装内に残っており、本書は metadata 処理が独立した common module に抽出済みとは記載しません。

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
