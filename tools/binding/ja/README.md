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
