# PCA合成年間デモ — Structured CSV

## 変換

| 項目 | 値 |
| --- | --- |
| 入力 | `../../original/PCA/PCA_synthetic_annual_demo.csv` |
| 変換 | `tools/uadc/flat_csv.py` |
| Binding | PCA 16列 Semantic Binding |
| CSV出力 | `PCA_synthetic_annual_demo_structured.csv` |
| Metadata出力 | `PCA_synthetic_annual_demo_structured.json` |

## 検証

| 項目 | 結果 |
| --- | ---: |
| Structured CSV行数 | 26,339 |
| Semantic roundtrip | 差異0 |
| Binding local_name | 38 / 38 |
| Binding fallback | 0 |
| HMD unresolved | 0 |
| Arelle | error 0 / warning 0 |

Metadataは、2026-12-31版のXBRL Japan XBRL GL Next experimental `cor` および `plt` namespaceを使用しています。

## 制約と状態

状態: Canonical WORKに配置した検証済み派生成果物です。本成果物は同梱するCSV/JSON pairおよび記載したtaxonomy versionを前提とします。本番会計データではなく、PCA社による認証または推奨を示すものでもありません。内部検証logおよびprivate referenceは、この公開instance directoryには含めていません。
