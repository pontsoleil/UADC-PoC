[English](../README.md) | **日本語**

# tools

## 目的

利用者向けの任意の評価・同期・tutorial program を保持します。

## 規則

`src/**` は規定 program と通常実行に必須の library を保持します。`tools/**` は任意の評価・tutorial・validation・同期用 tool、`tests/**` は検証 program です。`src/**` から `tools/**` を import してはいけません。

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
