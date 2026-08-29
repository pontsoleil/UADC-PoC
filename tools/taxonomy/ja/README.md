[English](../README.md) | **日本語**

# taxonomy

## 目的

この directory の Generator は UADC 内で評価するための同期 copy であり、第2正本ではありません。

## 正本

- Authority: `XBRL_GL_Next/tools/taxonomy/xBRLGL_TaxonomyGenerator.py`
- UADC synchronized copy: `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`
- Synchronized SHA-256: `9890946AEF8DD06C5B363605E6E951C27007C6932B4D0B3FB3C70807391BE651`

UADC 側の変更は承認済み XBRL GL Next release から同期し、source commit、source path、SHA-256 を記録します。

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
