[English](../README.md) | **日本語**

# tutorial

## 目的

tutorial wrapper は UADC 経路を説明するためのもので、規定 runtime 正本にはなりません。

## Program

- `semantic_binding_sample.py`
- `syntax_binding_sample.py`

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
