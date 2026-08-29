[English](../tuple_binding.md) | **日本語**

# tuple_binding

## 目的

`src/tuple_binding.py` は同一 HMD semantic model の Tuple XBRL ⇄ Structured CSV を変換します。semantic model 間の mapper ではありません。

## 保持要件

- selector and ordinal stability
- EE1 QName values
- nil state
- occurrence identity

## CLI

```text
py src/tuple_binding.py <input> --metadata <metadata.json> --hmd <hmd.csv> --qname-map <qname-map.csv> --taxonomy <entrypoint.xsd> --output <output> [--overlay <overlay.csv>] [--nil-manifest <file>]
```

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
