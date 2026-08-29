[English](../README.md) | **日本語**

# tests

## 目的

test は規定 src program と承認済み公開 tool を検証します。

## 実行

```text
py -m pytest tests
```

入力、code、設定、依存 version、成果物、validation scope が既に PASS した条件と materially 同一の場合は再実行しません。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
