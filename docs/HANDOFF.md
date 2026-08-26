# UADC_PoC Handoff

更新日: 2026-08-26 (JST)

## CII D16B formal promotion (2026-08-26)

- CEN/TS 16931-3-3:2020 Table 2に対する237/237行レビューと13件の訂正確認はPASSした。
- CII Bindingとgeneric runtimeはCanonicalとFormalでbyte-identicalである。
- 配置後検証は代表値380のCII順逆変換、XML Schema、semantic diff、およびSyntax Binding限定unit testに限定し、すべてPASSした。
- 同一前提の9コード往復、runtime/reference/identifier/cross-routeのaccepted evidenceは再利用し、不要な再実行を行っていない。
- 購入済みCEN/TS PDFおよびその抽出物はFormal repositoryへ含めていない。

## 前回作業の結果

- 最新公開baselineは`c504f88dab62a6e6e1248f1fbfa4eaaf169f81ac`である。
- 文書はenvironment、Structured CSV/LHM、Phase 1 UBL、Phase 2 ADS PSV、Phase 2 ADS XBRL GLの目的別構成へ整理済みである。
- Syntax Binding、Semantic Binding、Flat CSVの責務を分離し、共通概念の対応にはHMD `semantic_path`を使用する。

## 現在の注意事項

- WORKの主要実装はGIT baselineと異なるため、未検証のままGITへ一括同期しない。
- 実仕訳、取引先、口座、カード、税務情報、ローカル設定をGitHubへ登録しない。
- Binding Tableの意味をコードへ暗黙にハードコードしない。

## 次の作業

1. WORKとGITの主要実装差分を機能単位でレビューする。
2. XBRL-GL-Nextの正式HMD 2件とmanifestを、UADCのsemantic contractとして読み取り専用で接続する。
3. UADCの出力Structured CSVをLedgerExplorerの公開sample inputへ対応付ける。
4. XBRL-GL-Next → UADC_PoC → LedgerExplorerのintegration manifestを作成する。
5. 合成データで件数、semantic_path解決、反復、金額、税、document link、round-trip意味同等性を検証する。

## 未完了・未確認

- CII profile Schematronは今回のformal review scope外であり、未実行のままである。
- WORK差分の採否と全回帰テスト結果は未確定。
- LedgerExplorer向け正式column mappingは未作成。
- 連携検証で使用するXBRL-GL-Next commit／HMD SHAの固定方法は未確定。
