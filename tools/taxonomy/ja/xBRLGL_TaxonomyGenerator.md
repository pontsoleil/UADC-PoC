[English](../xBRLGL_TaxonomyGenerator.md) | **日本語**

# xBRLGL_TaxonomyGenerator

## 目的

これは XBRL GL Next taxonomy Generator の UADC 同期 copy です。

## fork 禁止

この copy を独自改訂しません。使用前に XBRL GL Next 正本との byte identity を検証します。

## CLI

```text
py tools/taxonomy/xBRLGL_TaxonomyGenerator.py --hmd-dir <hmd-dir> --output-dir <empty-output-dir> -n <namespace> --value-domain <domains.csv> --value <values.csv> --taxonomy-extension-overlay <overlay.csv> [options]
```

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
