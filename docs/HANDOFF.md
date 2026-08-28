# UADC_PoC Handoff

更新日: 2026-08-29 (JST)

## Public repository cleanup (2026-08-29)

- predecessor `19982b517e83b40845476d7a9bba49af336e31c4`のtracked 855件を全件分類し、200件をpublic Gitから削除した。
- 削除内訳はgenerated 179件、private one-time evidence 16件、duplicate 5件である。WORKの既存fileは削除していない。
- 削除対象200件はtask-local backupへ退避し、source/backup SHA-256の200/200一致を確認した。
- Markdownを正本とするgenerated PDF 13件、`out/cache/`、unreferenced analysis/render/extraction/smoke output、machine-local pathを含むArelle log、およびunreferenced `tests/evidence/`を削除した。
- current tests/docsが参照するPhase 1/2 output、taxonomy output、round-trip fixtureは保持した。
- text reference scanとSpecifications 5件のOOXML scanでは、削除対象へのunresolved active referenceは0件である。
- high-confidence credential/private-key signatureは0件、private IP findingは0件である。
- `docs/01_ENVIRONMENT_TESTS_TUTORIAL.md`と日本語版には各1件のmachine-specific user pathが残る。cleanupでは本文を改訂せず、別documentation changeとしてrepository-relative/generalized exampleへ変更する必要がある。
- `specs/ads/source/ADS_Definition_Tables.xlsx`は`HOLD_LICENCE`のまま保持した。redistribution evidenceの確認が必要である。
- program、Binding Table、入出力fixtureの内容は変更していないため、変換・round-trip testは再実行していない。

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
