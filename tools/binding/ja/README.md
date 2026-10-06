[English](../README.md) | **日本語**

# tools/binding

## 目的

この directory は、現在の UADC Binding／変換 runtime program と、それらに直接関係する supporting implementation を保持します。

## Core transformation runtime

- [`syntax_binding.py`](../syntax_binding.py) — XML ⇄ Structured CSV Syntax Binding。
- [`semantic_binding.py`](../semantic_binding.py) — 可逆な Structured CSV ⇄ Structured CSV Semantic Binding。
- [`flat_csv.py`](../flat_csv.py) — 登録済み profile、Binding、account mapping、tax mapping および関連 runtime definition を使用する Flat CSV ⇄ Structured CSV 変換。canonical 16-column Binding contract と、現行仕様に記載された登録済み compatibility handling を実装します。

これらの program は、HMD と Structured CSV semantic layer を中心とする binding stage を実装します。`tools/binding/` に存在することだけを、すべての UADC route に必須であることの根拠にはしません。

## Additional and supporting implementation

- [`selector_multiplicity.py`](../selector_multiplicity.py) — Semantic Binding runtime が import する selector-aware effective multiplicity support。
- [`aggregate_pairing.py`](../aggregate_pairing.py) — source slot と occurrence ownership を保持しながら、該当する Flat CSV conversion route で使用する aggregate pairing support。
- [`tuple_binding.py`](../tuple_binding.py) — 同じ HMD semantic modelに対する XBRL 2.1 Tuple ⇄ Structured CSV 変換。専用Tuple/OIM execution-manifest acceptanceはHOLDです。
- [`syntax_binding_ads_xbrl_gl.py`](../syntax_binding_ads_xbrl_gl.py) — 該当する route で使用する ADS/XBRL GL 固有の syntax conversion support。

[`support/`](../support/) は直接関係する supporting implementation と文書を保持します。[`tutorial/`](../tutorial/) は保持されている tutorial 文書であり、現行 runtime program を定義するものではありません。

現行 canonical tree に standalone `oim_metadata.py` は存在しません。OIM metadata handling は、該当する runtime implementation 内にあります。

## Optional review utility

[`tools/maintenance/csv_excel_bridge.py`](../../maintenance/csv_excel_bridge.py) は、review のための管理された CSV/XLSX interchange を提供します。core UADC transformation path の一部ではなく、Syntax Binding、Flat CSV Binding、Structured CSV generation、round-trip conversion の前提条件でもありません。現在登録されている `tests/runtime/**/RUN_PARAMETERS.json` case からは参照されていません。独立した用途は [CSV/XLSX bridge documentation](../csv_excel_bridge.md) を参照してください。

## Repository の責任境界

- [`tools/binding/**`](../) — UADC Binding／変換 runtime program と、それらに直接関係する supporting implementation。
- [`tools/taxonomy/**`](../../taxonomy/) — taxonomy generation program と supporting resource。
- [`tests/**`](../../../tests/) — validation と regression material。
- [`tests/runtime/**`](../../../tests/runtime/) — 登録済み runtime／reproducibility manifest。
- [`bindings/**`](../../../bindings/) — 該当する runtime route が使用する Binding、profile、account mapping、tax mapping および関連 definition。
- [`models/**`](../../../models/) — 該当する processing route で使用する semantic／HMD model input。

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test と再現性

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。

登録済み runtime／reproducibility case は [`tests/runtime/`](../../../tests/runtime/) に記録されています。各登録済み case では、その `RUN_PARAMETERS.json` を execution parameter authority とします。

## Formal OIM逆変換と負数の結果レポート

flat_csv.py to-flatは同一basenameのCSVを参照するFormal JSON metadataを入口とし、selector付き意味モデル再構成直後に負数monetaryAmountを検出します。入力ペア、仕訳・明細、selector semantic_path、側、取得科目、金額、MANUAL_REVIEW_REQUIREDを記録します。自動反転・絶対値化・科目変更はしません。

後続ConversionErrorでは既存--summary-logへ検出済み入力・実エラー・output_generated=falseを保存し、元例外/終了2を維持します。未生成出力の行番号・負数cell件数はnull、出力成功表示は付けません。

正常時はnormalized CSVの値・分割を保持し、SHAとsource対応を<normalized CSV>.conversion-report.jsonへ保存します。通常csv_physical_adapter.py from-uadcが自動sidecarを照合し、最終application CSVの行・物理行範囲・側・列・科目・金額・input fact IDを既存--reportと<application CSV>.conversion-report.jsonへ記録します。入力fact件数と分割後cell件数は別計数し、quoted multilineは物理行範囲で表します。試験専用finalizeなし。sidecarがないadapterは既存動作を維持します。

対象会計値を含むため非公開出力先で保持します。6DB HMDと税Mapping・物理形式は維持します。報告機能の採用と、税分類不足が残る実入力EPSON変換HOLDを区別します。

## EPSON45 公開用合成回帰ケース

専用登録: tests/runtime/epson/epson45-negative-report/RUN_PARAMETERS.json。Formal CSV/JSON fixture: instances/fixtures/epson45-negative-report/。両段階の通常CLIと相対パス・依存SHA・期待結果をmanifestへ登録。負数3 factから分割後4セル、最終application CSVの物理行と入力識別対応を検証。生成先outputs/は公開成果物ではなく、必要なら出力先だけ変更して実行する。

対応範囲は合成fixtureの報告回帰。旧pca-to-epson/epson-roundtrip/pca-roundtripは過去受入再現記録の現行HOLDで、現行成功経路とは扱わない。実入力EPSON45は税分類不足TAX_POLICY_UNRESOLVEDのHOLD。実EPSONアプリ取込は未受入。旧経路移行・税分類補完は別変更。
