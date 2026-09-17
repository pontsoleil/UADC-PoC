# UADC_PoC Handoff
## 2026-09-15 XBRL-GL-Next Tax Type successor adoption

- The accepted successor combines `cor:taxTransactionClassification` with `cor:taxType`; VAT and OTH remain distinct from Purchase/Sales, and OTH covers corporate and other non-consumption taxes.
- PCA and EPSON formal xBRL-CSV entry points passed Arelle 2.37.77 validation with 130,807 and 134,281 facts respectively, error 0/warning 0.
- Canonical UADC WORK now contains the accepted 22-file taxonomy subset, migrated accounting-entry CSV QName, and 400-row successor HMD. All 25 promotion targets match the accepted source SHA-256 values.
- Reuse this evidence for unchanged premises. Keep the missing EPSON tax-amount facts, `TAX_POLICY_AMBIGUOUS`, and EPSON application import as unresolved accounting/application items.
- Formal GIT, commit, and push were not performed.

## 2026-08-26 CII CEN/TS formal review and promotion handoff

- Use the 237-row Canonical CII D16B Binding at `specs/bindings/syntax/EN16931_CII_D16B_Invoice_Syntax_Binding.csv` (SHA-256 `B529F2585CA2A5FBFDAF673A6F96B98135CE274B8B022C1B791FF9863C23BD23`). Do not restore the old 34-row file or the uncorrected ChatGPT candidate.
- Use `src/syntax_binding.py` SHA-256 `4D9A163D157C223DCF5FDC68924A08D2BF9CF1AC745AA24D288E57ECF6FF7E3F`. Binding-declared F rows, predicates, alias-relative paths, transformations and XSD order are approved generic capabilities.
- CEN/TS 16931-3-3:2020 Table 2 governs forward syntax mapping. Table 3 supports inverse/coverage review. The purchased PDF remains outside Git.
- Gate A passed 237/237 and 13/13 with semantic-path errors, inverse ambiguities and prohibited hard-code all zero. Full roundtrip matrices with unchanged bytes are accepted predecessor evidence and must not be repeated without a changed precondition.
- Continue from the post-placement results and Formal commit/push record under `docs/ChatGPT/2026/202608/20260826/20260826_0957/cii-cen-ts-formal-review-promotion/outputs/`.

## 2026-08-23 Business Transactions terminology handoff

- Current BT HMD SHA-256: `4847717501FE9FA2305E9026F75A4FB992490D7228CA2364FEEE60F206ECB93C`.
- `BT05-02` is `Identification Scheme`; contextual local names end in `IdentificationScheme`.
- The flattened 25-file OIM closure, relative metadata URI and three-item subset are validated.
- Do not infer additional production Semantic Binding rows.
- Separate review: decide whether the older XBRL-GL-Next `FSM.xlsx` should be aligned to the accepted `FSM_btx.csv`.
- Formal GIT promotion remains a separate approval.

更新日: 2026-08-20 (JST)

## 前回作業の結果

- 最新公開baselineは`c504f88dab62a6e6e1248f1fbfa4eaaf169f81ac`である。
- 文書はenvironment、Structured CSV/LHM、Phase 1 UBL、Phase 2 ADS PSV、Phase 2 ADS XBRL GLの目的別構成へ整理済みである。
- Syntax Binding、Semantic Binding、Flat CSVの責務を分離し、共通概念の対応にはHMD `semantic_path`を使用する。

## 現在の注意事項

- WORKの主要実装はGIT baselineと異なるため、未検証のままGITへ一括同期しない。
- 実仕訳、取引先、口座、カード、税務情報、ローカル設定をGitHubへ登録しない。
- Binding Tableの意味をコードへ暗黙にハードコードしない。

## 2026-08-17 Canonical Flat CSV Word仕様書正本の整合

- 各文書系列のarchive及びprofile candidate snapshotを除く最新更新版を正本として選択し、次の3点を改訂した。
  - `research/pre-public-validation/UADC_Flat_CSV_Program_Specification.docx`
  - `research/pre-public-validation/UADC_Flat_CSV_Detailed_Program_Specification_2026-08-16.docx`
  - `Specifications/UADC_Transformation_Table_Specification.docx`
- `flat_csv.py`の役割、Canonical 17列Binding/HMDの使い方、`to-structured`／`to-flat`、keyed/marker grouping、source_rows variant、presence、max_occurs、変換、競合集計及び現行関数契約へ記述を整合した。
- 旧実行スクリプトの解説、比較表、旧dispatch図及び旧関数一覧を正本から除外した。旧3実装ファイル自体は変更・削除していない。
- PCA合成81列と青色申告合成25列CP932を含む既存23テストPASSの結果を反映した。実会計データは開いていない。
- DOCXは独立2回生成で各SHA-256が一致し、ZIP整合、再読込、目次field、section、style/theme/numbering/settings、図表連番、旧実行名0件を確認した。アクセシビリティ監査のhigh findingは0件で、mediumは意味表ではない1-cell containerだけである。
- `render_docx.py`は実行したがLibreOfficeが存在せずページ画像化できなかった。レンダーはSKIPであり、構造監査を代替実施した。
- WORKだけを変更した。GIT側コピー、stage、commit、push、public配置、外部接続及び本番操作は行っていない。

## 次の作業

1. WORKとGITの主要実装差分を機能単位でレビューする。
2. XBRL-GL-Nextの正式HMD 2件とmanifestを、UADCのsemantic contractとして読み取り専用で接続する。
3. UADCの出力Structured CSVをLedgerExplorerの公開sample inputへ対応付ける。
4. XBRL-GL-Next → UADC_PoC → LedgerExplorerのintegration manifestを作成する。
5. 合成データで件数、semantic_path解決、反復、金額、税、document link、round-trip意味同等性を検証する。

## 未完了・未確認

- WORK差分の採否と全回帰テスト結果は未確定。
- LedgerExplorer向け正式column mappingは未作成。
- 連携検証で使用するXBRL-GL-Next commit／HMD SHAの固定方法は未確定。
- 全件目録に記載した移動候補は未承認であり、既存ファイルの移動、名称変更、削除は未実施である。
- WORK直下の`.git`は空で、現在のWORKルートではGit状態をライブ確認できない。目録のGIT情報は別管理チェックアウトの作成時スナップショットであり、次回作業開始時に正規GITルートを別途確定する必要がある。

## 2026-08-14 PCA Accounting Entries binding改訂

- WORK内のPCA GL Binding Tableをレビュー用に改訂し、`EntryDetail[cor_DebitCreditIndicator="D"]`と`EntryDetail[cor_DebitCreditIndicator="C"]`の2種類を定義した。
- 各EntryDetailの配下には、selectorなしの通常`Subaccount`、`Subaccount[cor_Type="department"]`、`Subaccount[cor_Type="partner"]`を置く。`cor_Type="sub-account"`は使用しない。
- D/C及びType条件は`semantic_path`の述語だけに記載する。重複定義を避けるため、Binding Tableの`selector`列は全行空欄である。
- 正式なUADC Flat CSV Semantic Path Tableは18列、41行で構成する。内訳はGroup Definition Row 11件、PCA物理列30件（mapped 24件、extension-required 6件）であり、unmapped行及び固定値行は含めない。
- XBRL-GL-Nextの`semantic-model/LHM_for_taxonomy/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv`に対する未解決semantic pathは0件である。
- 6グループのselectorとHMD解決を定義だけで確認し、実会計データ・取引先マスタ値は成果物へ含めていない。
- 成果物は`docs/ChatGPT/2026/202608/20260814/20260814_1932/pca-xbrl-gl-next-subaccount-binding/outputs/`に置いた。GIT/GitHubへの操作は行っていない。

## 2026-08-15 WORK公開区分フレーム作成

- `research/`と`public/`の分類フレームを作成した。既存ファイルの移動はまだ行っていない。
- `research/programs/`をCommon Library、Syntax Binding、Semantic Table、Flat CSVの4種類に分け、各種類に仕様書、スクリプト、例題の入力・定義表・出力、テスト、マスタの受入先を作成した。
- `research/shared-resources/`にHMD、taxonomy、code lists、manifestの受入先を作成した。
- XBRL GL Next及びLedgerExplorerは別プロジェクトを正本とし、`research/integrations/`には参照契約とmanifestだけを置く方針とした。
- `public/`はサブディレクトリと説明READMEだけで構成し、公開対象ファイルは0件である。
- ルート`README.md`からUADC基礎資料、プロジェクト計画、research目録、共通マスタ、public領域を参照できるようにした。
- 全件目録を`research/shared-resources/manifests/UADC_PoC_full_file_inventory_20260815.xlsx`に作成した。SHA-256は`C41243397721A1A1B8B5254D80CA103F1FB80B085E216C8DA17FB5F8BA5BDA12`である。
- 目録はWORK 21,551件、別管理GIT側スナップショット1,629件を収録する。比較はsame 653件、different 93件、WORK-only 20,805件、GIT-only 883件である。
- Research Move Planは21,442件で、全件`inventory-only; not approved to move`である。全既存成果物は`research-unreviewed`、公開成果物は0件である。
- 目録には分類先、依存関係、Git状態、機密性、公開レビュー、参照更新要否を記録した。実会計データの内容は確認・転記していない。
- 次の作業は、全件一括移動を行わず、低リスクの小規模な候補群を選び、参照更新、機密性、ライセンス、再現性及び検証方法を含むファイル単位の移動計画を作成して承認を得ることである。

## 2026-08-15 操作終了時の安全チェックポイント

- WORK共通`AGENTS.md`と4プロジェクトの個別`AGENTS.md`へ、操作終了時の安全チェックポイントを追加した。
- 個々のコマンドではなく、承認された変更、テスト、GIT反映、本番反映等の一連の操作単位が終了した時に、状態変化に応じて引継ぎ文書を必要最小限更新する。
- 操作者が単独で「終わり」または明確な同義指示を出した場合は、作業途中でも同じチェックポイントを強制する。
- 通常終了及び「終わり」が追加承認するのは、必要な読み取り確認と`HANDOFF.md`、`CURRENT_BASELINE.md`、`DECISIONS.md`の必要最小限の更新だけである。
- 終了処理は、移動、名称変更、削除、再生成、外部アクセス、Git操作、公開、本番操作を承認しない。状態変化がない調査・質問回答では3文書を更新しない。
- 引継ぎ更新に失敗した場合や現状・機密性を確定できない場合は、完了扱いにせず停止理由を報告する。

## 2026-08-15 note記事作成

- ChatGPT Web、Windows版ChatGPT及びCodexの役割分担と、`AGENTS.md`による安全な操作ルールを一般化したnote掲載用Markdown記事を作成した。
- 配置: `docs/Codex/2026/202608/20260815/20260815_0830/chatgpt-codex-operation-boundaries/outputs/note_article.md`
- 主題: クライアント間でのMemory・文脈継承の限界、明示的な手順・禁止事項・停止条件、共通／個別`AGENTS.md`、操作終了時の引継ぎ。
- OpenAI DocsのChatGPT Web、desktop app、Memories、`AGENTS.md`ページを参照した。
- noteで表記法に依存しないよう、作業面別の役割分担はMarkdown表ではなく見出し付きリスト形式とした。
- 「では、`AGENTS.md`をどう作るか」を追加し、条件提示、AIによる草案作成、人間による確認・改訂、読み取りテスト、継続改善の手順と、再利用可能な草案依頼文を記載した。
- noteタイトル画像を`docs/Codex/2026/202608/20260815/20260815_0830/chatgpt-codex-operation-boundaries/outputs/note_title_1280x670.png`へ作成した。寸法は1280×670px、SHA-256は`685F1EA6AC73E35557B0215AB26CC805B0478AE8F899771779D8AE1127B8976B`である。
- 固有プロジェクト名、実会計データ、個人情報、認証情報は記事へ含めていない。公開、Git操作、noteへの投稿は未実施である。

## 2026-08-15 GIT公開構成移行前バックアップ

- 正規GITチェックアウトを`C:\Users\nobuy\GitHub\GIT\UADC-PoC`と確認した。remoteは`https://github.com/pontsoleil/UADC-PoC.git`、branchは`main`、確認時HEADは`11acc49b1c9458b667b451ec41ccb2aedaf5ccb4`で、作業ツリーはcleanだった。
- 移行前保全として、`git ls-files`で得た追跡対象705件を`private/backups/git-pre-public-layout/20260815_093156/`へコピーした。`.git/`及び未追跡ファイルは含めていない。
- コピー元とバックアップ先の各ファイルをSHA-256で照合し、705件すべて一致した。追跡対象の合計サイズは26,483,631 bytesである。
- バックアップ目録は`private/backups/git-pre-public-layout/20260815_093156/GIT_SNAPSHOT_MANIFEST.csv`で、同ファイルのSHA-256は`EDF5A7F4E0994B6BB354D35690E022839004849FE6D745D916056A70ED23F4CF`である。
- 公開構成の対応は、`WORK/UADC_PoC/public/<relative-path>`を`GIT/UADC-PoC/<relative-path>`へコピーする方式とする。GIT側に`public/`を一段追加する方式ではない。
- 現在の`public/`は説明README 8件だけで、公開成果物は未配置である。この状態をGITへディレクトリ同期すると既存追跡ファイルの大半を欠落させるため、同期は行っていない。
- 初回文書候補のうち、`LICENSE-CODE`、`LICENSE-CONTENT`、`LICENSE-SCOPE.md`及び`THIRD_PARTY_NOTICES.md`は`public/`に同名競合がない。ルート`README.md`は`public/README.md`の公開準備ルールと内容を統合してからレビューする必要がある。
- WORKの`AGENTS.md`にはローカル絶対パス等が含まれるため、そのまま公開しない。GIT側`AGENTS.md`の旧Git手順も、共通ルールと整合する公開用文面へ改訂してから反映する。
- GIT側へのファイルコピー、既存ファイルの移動・削除、stage、commit、pushは未実施である。次は、WORK側`public/`に初回候補を作成し、機密性、ライセンス、リンク及び差分を確認したうえで、ファイル単位のコピー承認を得る。
- GIT側の`README.md`及び`README.pdf`はプロジェクト全体の記述として保存対象に指定された。`README.mdf`は存在しないため`README.md`の誤記として扱い、2件を削除・機械的一括上書きから保護する。

## 2026-08-15 GIT側AGENTS.mdのWORK規則との整合

- `C:\Users\nobuy\GitHub\GIT\UADC-PoC\AGENTS.md`を、WORK共通及びUADC個別の安全規則と整合するよう更新した。
- WORK/GITのディレクトリ同期禁止、ファイル単位`COPY_PLAN`、既存変更の保護、コピーとGit操作の承認分離、明示されない削除・名称変更の禁止を追加した。
- 実会計データ、個人・取引先・口座情報、認証情報、非公開資料及び未承認の生成・検証成果物をGit・GitHubへ登録しない規則を追加した。
- Syntax Binding、Semantic Table、Flat CSVの区別、`semantic_path`の扱い及びBinding Table外への暗黙なハードコード禁止を追加した。
- 旧手順の`git add -A`を削除し、明示承認されたパスだけをstageして`git diff --cached`で確認する手順へ変更した。stage、commit及びpushは現在の依頼でそれぞれ明示された場合だけ実施する。
- `README.md`及び`README.pdf`の保存、操作終了時の安全チェックポイント、3記録文書の必要最小限更新を追加した。
- GIT作業ツリーでは`AGENTS.md`だけが未コミット変更であり、stage、commit、pushは行っていない。プログラム、Binding Table、入力、出力及びテストデータは変更していない。

## 2026-08-15 PCA会計Semantic Binding公開方針

- PCA会計CSVとXBRL GL Next Accounting Entries Structured CSVの対応定義は、Transformation Table Specification準拠の`Flat CSV Semantic Path Table`として、未完部分を含む`Development Draft`でWORK側`public/`へ配置し、公開候補としてレビューする方針となった。
- 開発・改訂・検証は`Specifications/`、`src/`、`tests/`等のWORK側`public/`外にある開発元で実施する。`public/`は開発正本ではなく、内容、機密性、ライセンス、依存関係及び検証状態を確認できたファイルのコピー受入れ場所とする。
- 機能的に未完でも、公開可能性を確認し、`Development Draft`、未対応範囲及び未実施検証を明記できる成果物は`public/`へコピーできる。WORK側`public/`への配置はGIT登録を意味せず、完成・検証済みとなったファイルだけを、別途ファイル単位の承認を得てGITへ登録する。
- 公開正本候補は`Specifications/UADC_Transformation_Examples/Journal_Entry/cor_Accounting_Entries_PCA_GL_Flat_CSV_Semantic_Path_Table_20260814.xlsx`である。現物は`Flat_CSV_Table` 1シート、17列、28データ行で、現行Transformation Table Specificationの17列定義と一致する。
- 以前の引継ぎにある「18列、41行」は現行仕様書及び現物と一致しないため、公開判定には使用しない。17列を正とし、行数は対応範囲の拡張に伴って増減し得る。
- 現物にはmappedとextension-requiredが混在している。公開前に`Development Draft`表示、仕様版、参照HMDの版・SHA-256、対応状況、未実装テストを明記し、private由来のパスや例示値がないことを再検査する。
- 旧81行Binding、`sub-account`型・固定値行を含む旧レビュー版、parameter JSON、inspect NDJSON及びpreview画像は公開正本から除外する。
- WORK側`public/`へのコピー、GIT側への反映、stage、commit、pushはまだ行っていない。

## 2026-08-15 publicコピー前検証領域の整備

- `research/pre-public-validation/`を作成し、`invoice-en16931-syntax-binding/`と`pca-xbrl-gl-next-flat-csv-binding/`の2ケースを整備した。ルート`README.md`から入口を追加した。
- 各ケースを`candidate/`、`source-references/`、`test-work/`、`review/`へ分離した。`candidate/`は公開候補スナップショット、`source-references/`は旧版・第三者由来・未統合資料、`test-work/`は生成結果・逆変換・比較・ログ、`review/`はテスト・公開判定・コピー台帳である。
- 既存ファイル33件を元の場所に残したままコピーした。内訳はinvoice/EN 16931候補12件・参照8件、PCA候補3件・参照10件である。全33件でコピー元・先SHA-256が一致し、コピー元が残っていることを確認した。
- invoice/EN 16931ケース全体は31ファイルで、candidate 18件、source-references 8件、review 4件、ルートREADME 1件である。PINT候補は現行UBL baselineであり、PINT固有適合は未確認である。SME Common EDI候補表は未作成で、legacy bindingとtrial XMLを参照領域に置いた。
- PCAケース全体は27ファイルで、candidate 10件、source-references 10件、review 6件、ルートREADME 1件である。候補定義表は17列・28データ行で、mapped 8件、extension_required 18件、Group Definition Row 2件である。変換スクリプト、合成入力、期待出力、専用テストは未作成としてREADMEへ明記した。
- `review/COPY_PLAN.csv`と`review/SHA256SUMS.csv`を各ケースに作成した。33件のコピー不一致は0件である。
- candidate配下のテキスト及びDOCX/XLSX 4件の内部XMLを、ローカル絶対パス、private参照、`README_PRIVATE`等で走査し、該当0件だった。parameter JSON、inspect NDJSON、review preview画像、実会計データ及びmasterはコピーしていない。
- 既存UBL baselineの階層型forward、reverse及び当時の旧横持ち抽出テストを実行した。旧横持ち抽出テストは後続作業で廃止・削除したため、現在の正式テスト証跡には含めない。
- テストにより`out/phase1/`、`out/reverse/`及び`out/structured/`の既存生成物7件が再生成された。正式baseline、`public/`及びGIT側への反映は変更しておらず、stage、commit、pushも行っていない。

## 2026-08-15 TEST_PLAN統合

- Invoice EN 16931 Syntax BindingとPCA/XBRL GL Next Flat CSV Bindingの各`review/TEST_PLAN.md`を作成し、既存README、TEST_RESULTS、PUBLICATION_CHECKLIST、COPY_PLAN、SHA台帳及びPCAの未解決・機密性資料を統合した。
- Invoice計画は共通構造・公開前検査、PINT/UBL、SME Common EDI/CII、profile間比較を分離し、fixture方針、前提、ケースID、実施順序、合格基準、現状及び停止条件を定義した。
- PCA計画は17列表契約、HMD解決、Group Definition、D/C occurrence、extension-required、forward、reverse、round-trip、決定性、negative test及び証跡要件を定義した。
- 両計画で、未完でも公開可能性を確認したDevelopment DraftをWORK側`public/`へコピーする条件と、完成・検証済み成果物だけをGITへ登録する条件を区別した。
- Invoice TEST_PLANは162行、SHA-256 `06BD8F3955C4E6F557ECDD20860FD23E1F6D8860CFF293C78D38A59E5734A29C`、PCA TEST_PLANは197行、SHA-256 `6CED8F05ED2AD59540575132DAB9931BFA38EEE73FF560BBBF1622D08123A54D`である。
- 各ケースREADMEからTEST_PLANへの入口を追加し、PUBLICATION_CHECKLISTへ計画作成済みを反映した。SHA台帳を再生成し、既存33コピーのSHA不一致0件及びコピー元残存を再確認した。
- 今回は計画文書の作成のみで、新しい変換テスト、`public/`コピー、GIT側変更、stage、commit、pushは行っていない。

## 2026-08-15 Invoice Structured CSV逆変換形式確認

- OpenPeppol最小入力から生成済みの2種類のStructured CSVについて逆変換対応を確認した。
- 9行・177列の階層型`out/phase1/openpeppol_ubl_invoice_minimal.csv`は、現行reverse converterで87値のUBL XMLへ復元でき、UBL 2.1 schema validationは0 errorでPASSした。
- 旧1行・197列の横持ち抽出CSVは5値しか逆変換できず、UBL 2.1 schema validationで3 errorだった。数量値への単位誤対応と必須sequence欠落を確認した。
- 現状のreverse converterが対応する正式round-trip入力は、dimension列を持つ9行・177列の階層型Structured CSVである。旧1行・197列形式及びlegacy 1行・196列形式は、後続作業で生成スクリプト、結果、専用テスト及び診断用XMLを削除した。
- SHA台帳再生成時、作業中に新たに存在した`research/pre-public-validation/invoice-en16931-syntax-binding/candidate/shared-resources/hmd/EN16931_CIUS_Invoice_LHM.xlsx`が別プロセスで使用中のため読取り不能だった。このファイルは今回配置した33コピーに含まれず、内容・SHA・公開可否は未確認である。ファイルには触れず、現在の`SHA256SUMS.csv`はこの1件を含まない33行のため、ロック解除後に所有者と用途を確認して再生成する必要がある。

## 2026-08-15 旧横持ち抽出の撤去とPINT Japan例の追加

- 旧tutorial Syntax Bindingスクリプト、専用テスト、1行196/197列の横持ちCSV、失敗診断XML及び検証領域内のコピーをWORKから削除した。関連README、仕様文書、manifest、package builder、COPY_PLAN及びSHA台帳の参照も除去した。
- `pint-jp-resources-dev (11).zip`の`trn-invoice/example/`からPINT Japan UBL Invoice例9件を`samples/input/pint-jp-examples/`へコピーした。元ZIPは変更していない。ZIP SHA-256は`2D0BB36C14106649F8C14C3E2377C0BD027FB434BD908AFEB06900EE620AA570`である。
- 入力9件はすべてUBL 2.1 schema validationにPASSした。`CustomizationID`は`urn:peppol:pint:billing-1@jp-1`、`ProfileID`は`urn:peppol:bis:billing`である。
- `tests/test_pint_jp_examples_conversion.py`を追加し、9件すべてのforward変換がPASSした。出力は177列、4～20階層行で、請求書番号、文書通貨、明細識別子及び支払総額を確認した。
- round-trip fixture生成をPINT Japanへ拡張し、OpenPeppol 1件、BIS Billing 3が9件、PINT Japan 9件の合計19件について`tests/test_roundtrip_artifacts.py`がPASSした。同じforward変換を2回実行し、CSV/metadata 18ファイルのSHA-256不一致は0件だった。
- 逆変換XMLのUBL 2.1 schema validationは、PINT Japan最小例1件がPASS、残る8件がFAILした。7件は添付関連属性、1件は`TaxRepresentativeParty`の必須sequence復元が原因である。PINT base/Japan jurisdiction Schematronは未実施であり、PINT適合をまだ表明しない。
- 最終回帰時、`out/phase1/openpeppol_ubl_invoice_minimal.csv`が別プロセスでロックされ、既存`test_syntax_binding.py`及び`test_syntax_binding_reverse.py`の再実行は未完了となった。ロック解除後に再実行する。
- 実会計データは使用していない。`public/`、GIT側、stage、commit、pushは操作していない。
- 次の開始点は、添付属性と`TaxRepresentativeParty`のround-trip復元修正、19件のUBL schema再検証、配布ZIP内SchematronによるPINT Japan profile検証である。

## 2026-08-15 UBL構文順及び必須syntax-only既定値の改定

- `specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv`へ`syntax_sequence`を第2列として追加し、UBL 2.1 XSD定義順から199/199行を設定して物理的にも同順に整列した。
- 同表へ`default_value`列とsyntax-only固定値行2件を追加した。`EmbeddedDocumentBinaryObject/@mimeCode`及び`CardAccount/NetworkID`を対象とし、`type=F`、`const:` semantic path、`default_value=NA`で定義した。
- `src/syntax_binding.py`を改定し、逆変換時に`syntax_sequence`順で処理する。syntax-only既定値は対象親構造が既に存在する場合だけ補完し、Attachment又はCardAccount等の存在しない業務構造を作成しない。
- `cbc:ChargeIndicator=false()`／`true()`等のXPathリテラル述語は、従来どおりコンテキスト生成時に値を実体化する。syntax-only既定値とは別の仕組みであり、独立したHMD項目又は既定値行を必要としない。
- `Specifications/UADC_Transformation_Table_Specification.docx`及び`Specifications/UADC_Syntax_Binding_Program_Specification.docx`へ、`syntax_sequence`、syntax-only固定値行、親存在時だけの補完、構造新規作成禁止及びセレクター固定値との区別を反映した。DOCX内部構造と本文抽出は確認したが、環境にLibreOfficeがないためページ画像による目視レイアウト確認は未実施である。
- 英日Phase 1手順書、テストREADME及び設計判断D-013も同じ規則へ更新した。
- 回帰結果は、Binding順199/199 PASS、round-trip成果物19/19 PASS、逆変換UBL 2.1 schema 19/19 PASS、添付7件及びCardAccount 1件の条件付き`NA`補完PASS、`ChargeIndicator` 38値PASS、Python compile PASSである。実会計データは使用していない。
- 以前のPINT Japan逆変換8件FAILは解消した。残る適合確認はPINT base及びJapan jurisdiction Schematronであり、UBL schema PASSだけでPINT適合とは表明しない。
- `out/phase1/openpeppol_ubl_invoice_minimal.csv`が別プロセスによりロック中のため、同ファイルへ書き込む既存`test_syntax_binding.py`及び`test_syntax_binding_reverse.py`の再実行は未完了である。
- pre-public candidateは今回更新していないため、現行開発元との差分がある。ロック中で未確認のcandidate HMD XLSXにも触れていない。`public/`、GIT側、stage、commit、pushは操作していない。

## 2026-08-15 UN/CEFACT CII 100.D16B Syntax Binding forwardテスト追加

- EN 16931公式検証リポジトリの固定commit `b6c9e06a59812fb1a83585da40923b3678a649ad`から、UN/CEFACT CrossIndustryInvoice 100.D16B SCRDM Subsetのuncoupled/decoupled-code-list XSD 54件と公開XML 3件を取得した。UN/CEFACT直接ZIP URLはHTTP 403だったため、実際の取得元をREADMEへ明記した。
- XSDは`out/cache/CII-D16B-SCRDM-Subset/uncoupled-clm/CII/`へ相対構造を維持して配置した。公開XML原本は`samples/input/cii-d16b-examples/`へ変更せず配置し、派生入力は作成していない。
- `specs/bindings/syntax/EN16931_CII_D16B_Invoice_Syntax_Binding.csv`を追加した。34行すべてが`specs/lhm/EN16931_CIUS_Invoice_LHM.csv`の既存semantic pathへ解決し、CII XSD由来`syntax_sequence`も34/34解決する。HMDパスの推測追加はない。
- 初期範囲は請求書番号、文書種別、発行日、通貨、売手・買手、明細、商品名、数量・単位、単価、明細金額、明細税区分・税率、ヘッダー税内訳、行合計、税抜・税・税込・支払金額である。
- `tests/test_cii_d16b_conversion.py`を追加した。XSD参照54/54、公開XML検証3/3、Binding HMD/XSD整合34/34、forward 3/3、明細・税内訳反復、任意値欠損及び2回実行決定性がPASSした。
- 出力は`out/phase1/cii-d16b/`にCSV及びmetadata各3件。`CII_business_example_01.xml`は明細5・税3・9行、`CII_example1.xml`は明細20・税2・23行、`CII_example6.xml`は明細3・税2・6行である。
- `CII_example6.xml`の税内訳は、`1500/S/25/375`と`2500/S/12/300`が別の`dVatBreakdown` occurrenceとして入力順に出力され、各4項目の所属を保持した。
- `tools/update_lhm_syntax_sequence_from_ubl_xsd.py`をローカル要素・`xsd:choice`・任意namespace mapへ対応させ、既存UBL順テスト199/199もPASSした。
- 既存Syntax Binding回帰は`test_syntax_binding.py`、reverse、PINT Japan、roundtrip、UBL schema、binding sequence、schema child orderの7件すべてPASSし、ロック問題は解消していた。
- READMEへスキーマ・XMLの取得元、固定commit、取得日、版、ライセンス及びSHA-256を記録した。詳細報告は`docs/Codex/2026/202608/20260815/20260815_1317/cii-d16b-syntax-binding/outputs/REPORT.md`にある。
- 未完了は、CII `DateTimeString format="102"`のISO日付正規化、CII reverse、EN 16931 CII Schematron、初期34行外の項目及びcandidate snapshot更新である。これらをPASSとして扱わない。
- 実会計データは使用していない。ファイル移動・削除、`public/`、GIT側、stage、commit、pushは操作していない。

## 2026-08-15 XBRL GL Next Accounting Entries HMD参照配置

- 操作者指定により、`C:/Users/nobuy/GitHub/WORK/XBRL-GL-Next/semantic-model/LHM_for_taxonomy/`を最新版の正本と確定した。
- 同ディレクトリのAccounting Entries HMD、Business Transactions HMD及び`manifest.csv`を、`research/pre-public-validation/pca-xbrl-gl-next-flat-csv-binding/source-references/`へコピーした。既存Accounting Entries旧スナップショットは最新版で置換し、他の旧参照資料は削除していない。
- 18列契約は2/2 PASS。Accounting Entries 398行、Business Transactions 433行で、`semantic_path`、QName、XPath重複は各0件、manifestの行数・SHA-256と一致した。
- ケースREADME、`review/COPY_PLAN.csv`及び`review/SHA256SUMS.csv`を最新版の所有元とハッシュへ更新した。
- `public/`、GIT側、stage、commit、pushは行っていない。次のPCA Binding検証ではこの3ファイルセットを参照する。

## 2026-08-15 PCA Flat CSV表の最新HMD対応

- ChatGPTが指摘した40行表を、最新版398行Accounting Entries HMDで再照合した。旧表は削除・上書きせず、38行の改訂CSV/XLSXをCodex成果物とpre-publicの`source-references/`へ追加した。
- Account、Subaccount、Taxは最新HMDに存在するため、旧220行HMDを前提とした「HMDに存在しない」という指摘は解消した。38/38行がselector除去後のHMDへ一意に解決し、主要属性も一致する。
- `Detail Description`は現行ID `CO21-30`、Debit/Credit Indicatorは`CO21-34`、Detail Account Identifierは`CO21-29`、Subaccountは`CO17-15`、Detail Taxは`CO21-27`を使用する。
- `cor_DetailSubaccount`は`cor_Subaccount`へ置換し、補助科目Typeは`auxiliary-account`とした。D/C及びSubaccount Typeのpredicate値は明示的な`default_value`行から生成する。
- PCA税区分名2行はXBRL GL Next `Tax Description`と意味が異なるためBindingから除外し、税マスターenrichment又は統制された拡張を未完了事項とした。
- Transformation Table Specification及びFlat CSV Program Specificationを、`[condition]`、HMD selector除去、occurrence identity、predicate source、reverse時の不要構造生成禁止及び税区分名方針へ改訂し、pre-public candidateの仕様書コピーも整合させた。
- 正規スクリプトは`csv2tidy.py`と`tidy2csv.py`。現存private版は旧13列Binding interfaceで、今回の17列改訂表を直接読めない。次回は両スクリプトの17列adapter/refactor、合成fixture、forward/reverse/round-trip/negative/determinism testを実装する。
- 静的テスト`tests/test_pca_flat_csv_hmd_binding.py`はPASS。改訂XLSX目視QAとCSV/XLSX決定性はPASS。DOCX構造QAはPASS、ページ画像QAはLibreOffice不在で未実施。
- 既存28行candidate workbookは別スコープのため上書きしていない。38行レビュー表との統合方針を決めてからcandidate正本を更新する。
- 実会計データは使用していない。ファイル移動・削除、`public/`、GIT側、stage、commit、pushは行っていない。

## 2026-08-15 PCA Flat CSV物理列一意化

- 操作者指示により、Semantic Binding表の非空`column`を固有CSVテーブルの物理列定義へ一致させ、重複を禁止する方針へ改訂した。
- `csv2tidy.py`／`tidy2csv.py`は固定13列を位置読取りし、`column`辞書で後勝ち上書きする。`fixedValue`は実処理で未参照、旧14列目のexample値は余剰データになる。現行legacy表の実読取り値はforward 87 key/81物理列、reverse 32 row/26物理列である。
- 最新表は`PCA_GL_XBRL_GL_Next_Flat_CSV_Table_shared_detail_20260815`。37行、PCA physical ID `ColumnN`を20件使用し、重複0件、最新HMD解決37/37件である。表示行は物理Column順を基本とし、Tax CategoryとAmount of Taxesを連続配置する。`sequence`は最新版HMDの値をそのまま使用する。出力はPCAのD occurrence group、C occurrence groupの順にまとめ、各group内をsequence昇順とする。D/C横断の単純sort及びXMLスキーマ順は本表では扱わない。
- 元CSVにはEntryDetail列がないため、共通EntryDetailテンプレートを1行だけ定義し、selector付きの側別項目だけをD/Cへ分けた。Column14/25はD/C Monetary Amount、Column15/26は各DetailTaxのAmount of Taxesである。
- EntryHeaderは`Column2`でgroupingする。明細はLine Number列を仮定せず`source_rows`でD/C Detailを各1件生成し、借方だけをreverse driverとする。
- 共通摘要`Column27`は共通テンプレートへ一度だけ定義し、forwardではD/Cへ継承する。reverseで複数非空値がある場合は後処理値で上書きし、エラー停止せず、終了時ログに対象columnと件数だけを集計する。旧`tidy2csv.py`にも順次代入による後勝ち挙動はあるが集計ログはない。
- Transformation Table SpecificationとFlat CSV Program Specificationへ、非空物理列の一意性、`source_rows`、driver/group pairing及び`PHYSICAL_COLUMN_DUPLICATE`を追加した。
- 次回は、両スクリプトをlist-based Bindingへ変更し、17列adapter、最新HMD path、`source_rows`、81列reverse layout及び合成fixtureの往復テストを実装する。
- 既存28行candidate及び以前の38行review snapshotは上書きせず履歴として残した。`public/`、GIT、stage、commit、pushは未操作である。

## 2026-08-15 PCA Flat CSV canonical converter実装・往復検証

- 目的: backup取得後、`csv2tidy.py`／`tidy2csv.py`を最新版17列Bindingへ対応させ、forward、reverse及び往復変換を検証する。
- backup: `docs/Codex/2026/202608/20260815/20260815_1631/pca-flat-csv-converter-implementation/outputs/backup/`へ変更前の両スクリプト、shared-detail Binding、Transformation仕様書、Flat CSV Program仕様書を保存した。
- 実施結果: `flat_csv_canonical.py`を追加し、両entry pointはcanonical 17列headerだけを新経路へdispatchする。旧13列readerは維持した。
- canonical loader: 17列完全一致、非空物理column一意性、`ColumnN`形式、selector除去後HMD解決、Binding/HMD sequence一致及び単一`source_rows` driverを検証する。
- forward: 合成81列2行を75行のcanonical tidyへ変換。各source rowをD→Cの順でまとめ、各occurrence内をHMD sequence順に出力し、共通Column27を両側へ継承した。
- reverse: 75行からheaderless 81列2行を復元。共通columnの複数非空値は後処理値で上書きし、終了時JSONへcolumnと件数だけを記録する。
- テスト: forward/reverse、完全往復、各方向2回の決定性、D/C順、sequence順、Column27競合、legacy dispatch/read-count回帰がPASS。source/reverse SHA-256は同一。Python compile PASS。旧コードの既存invalid-escape `SyntaxWarning` 2件は未修正。
- 証跡: `docs/Codex/2026/202608/20260815/20260815_1631/pca-flat-csv-converter-implementation/outputs/test-run/test_result.json`。合成データだけを使用し、private PCA実データは開いていない。
- 文書: Transformation Table Specification、Flat CSV Program Specification、pre-public README、tests/scripts README、TEST_RESULTS、UNRESOLVED_FIELDS、PUBLICATION_CHECKLIST、COPY_PLAN及びSHA台帳を更新した。DOCXはpackage/reopen/required-text検査PASS。LibreOffice不在のためページ画像QAは未実施。
- 未完了: datatype・借貸balance、unsupported 81列のloss分類、malformed occurrence、encoding境界等のnegative/boundary一式、candidateへの実装本体及び合成fixtureの正式昇格、privacy/licence review、`public/`コピー、GIT登録。
- 次の開始点: `test_canonical_roundtrip.py`へ上記negative/loss testを追加し、公開候補へ含める実装・fixtureをファイル単位で確定する。
- 状態: WORK/private及びpre-publicだけを変更。ファイル移動・削除、`public/`、GIT側、stage、commit、push、本番操作は行っていない。生成された`__pycache__`は公開対象外とする。

## 2026-08-15 匿名package化とBinding駆動genericization

- 目的: 現行vendor固有名を英語の匿名package名へ変更し、完了後に物理key及びvariantのprogram固定を除去する。
- 採用名: package `generic-journal-entry-flat-csv`、profile `anonymized-accounting-csv-81`、表示名 `Generic Journal Entry Flat CSV`。
- 対象外: 過去版、archive、旧vendor package、旧Binding、過去作業記録、旧生成物及びbackup。これらは名称・内容・配置を変更していない。
- backup: 現行対象36ファイルを連番付き短縮名で保存し、`BACKUP_MANIFEST.csv`へ元相対path、SHA-256、backup SHA-256を記録した。不一致0件。最初の相対path保持方式はWindows path長で停止し、元ファイル変更前に短縮方式へ切替えた。途中copyは削除していない。
- package: `research/pre-public-validation/generic-journal-entry-flat-csv/`を新設し、現行37行Binding、HMD、仕様書、test、review文書だけを匿名化して配置した。過去表はコピーしていない。
- genericization: `flat_csv_canonical.py`のColumn2固定を`keyed_rows.group_key`読取りへ、D/C固定をsource_rows driver直下selector variantのBinding宣言順読取りへ変更した。
- test: 匿名profileのD/C往復、81列完全一致、決定性、Column27競合集計がPASS。さらにColumn3 keyとLEFT/RIGHT variantの派生Bindingで完全往復PASS。旧13列判定は合成headerだけで確認し、private inputを開いていない。
- workbook: 4sheetをartifact-toolで読取り、匿名化、formula error scan 0、全sheet render目視PASS。Office内部XMLのvendor名残存0件。
- DOCX: 現行2仕様書と新package copiesを匿名化・genericization整合。package/reopen/text検査PASS。LibreOffice不在のためpage-image QAは未実施。
- 未完了: unsupported列loss分類、datatype・借貸balance、malformed occurrence、複数nested keyed group、複数driver及びencoding境界test。candidate scripts本体／fixtureの正式昇格、privacy/licence最終判定、`public/`及びGIT登録も未実施。
- 次の開始点: `flat_csv_canonical.py`の単一keyed header／単一driver制約を、明示的なnested occurrence modelへ拡張し、negative/loss testを追加する。
- 状態: 実会計データ、ファイル削除、`public/`、GIT側、stage、commit、push、本番操作は行っていない。

## 2026-08-15 Yayoi 25-column Semantic BindingとCanonical汎用化

- 目的: 指定された弥生青色申告journal exportへSemantic Bindingを定義し、同profileを外部定義だけで処理できるよう`flat_csv_canonical.py`を汎用化する。
- 原本保護: raw原本を変更せず、`private/input/working/`へSHA一致copyを作成して調査・変換した。実値は公開文書、task output、チャットへ記録していない。
- 入力確認: CP932、headerless 25列、244物理行。Column1は全244行がsingle markerでmarker sequence error 0。複合markerは合成fixtureで検証した。
- Binding: `research/pre-public-validation/generic-journal-entry-flat-csv/profiles/yayoi-blue-return-journal-25/binding/`のCSV/XLSX、35行。最新版Accounting Entries HMDへ35/35解決し、新規Semantic Pathは推測追加していない。
- 実装: `marker_rows` state machine、variant presence、optional Class suppression、正逆transform registry、CP932 physicalとUTF-8 definition/tidyのencoding分離を追加した。entry pointsは`--input-encoding`／`--output-encoding`を追加し、旧`--encoding`を維持した。
- 実データ結果: 244/244 source rowを244 journal groupへ変換し、D/C occurrence各244、row-level貸借不一致0、forward 2回一致。reverseはBinding対象列及びColumn1制御列で一致した。
- 意味差: Column20/23/24/25の各244非空値、計976 cellは未結合制御値としてreverse loss。全25列の完全往復とは表明しない。Column3/18/20/21/22/23/24/25及び標準税Code Mappingが未解決。
- 回帰: 匿名81列profileの完全往復、Column3 key＋LEFT/RIGHT variant、Python compile PASS。legacy codeの既存invalid-escape SyntaxWarning 2件は残る。
- 文書: Transformation Table Specification、Flat CSV Program Specification、profile README、TEST_PLAN/RESULTS、UNRESOLVED、private inventory/work log、baseline、decisionsを更新した。XLSX 4sheetは目視PASS。DOCXは構造QA PASS、LibreOffice不在でpage-image QA未実施。
- 次の開始点: Column20/23/24/25のsource制御値を「保持対象」「canonical再生成可能」「破棄可能」に分類し、Column3/18/21/22も業務意味を確認する。その後、税区分Code Mappingと複合仕訳の実exportでの検証へ進む。
- 状態: WORK/private及びpre-public Development Draftだけを変更。実入力・生成物はprivate限定。削除、`public/`、GIT、stage、commit、push、本番操作なし。WORKはGit repositoryでないためGit追跡状態は確認不能。

## 2026-08-15 青色申告CSV匿名化・英語摘要化

- 目的: `private/input/raw/`の実会計CSV原本を保持し、同じフォルダへ英語名の匿名化コピーを作成する。
- 入出力: CP932、CRLF、カンマ区切り、ヘッダーなし25列、24レコード。出力は`2026-04_accounts_payable_entries_en.csv`。
- 匿名化: 補助科目に含まれる相手先等2種類を決定的な英語疑似名へ置換し、摘要24件を英語の一般化された費目表現へ置換した。実名・実摘要・金額は本書へ記載しない。
- 検証: レコード数、全行列数、順序、区切り、文字コード、改行、日付、金額、税区分及び全非対象フィールドの一致を確認。摘要は全件ASCII英語。2回生成の決定性もPASS。
- 原本保護: 処理前後の原本SHA-256一致を確認し、原本は未変更。匿名化出力を含む`private/`はGit・GitHub・`public/`の対象外とする。
- Binding方式: 変換Bindingは使用せず、弥生系ヘッダーなし25列journal exportの物理列位置に基づく匿名化のみを実施した。Structured CSV変換及び往復変換は対象外。
- 追加入力: 同形式の244レコードを処理し、`fiscal_2026_journal_as_of_2026-07-04_en.csv`を追加した。補助科目の固有名候補7種類を英語疑似名へ置換し、入力済み摘要235件を英語化、元の空欄9件は空欄のまま保持した。
- 追加検証: 244レコード、全行25列、順序、CP932、CRLF、カンマ区切り、日付、金額、税区分及び全非対象フィールドの一致、摘要のASCII化、2回生成の決定性、原本未変更を確認した。

## 2026-08-16 AGENTS.md共通統制の整備

- 目的: XBRL-GL-NextとUADC_PoCの個別指示を比較し、不足していたbackup、失敗時対応、再現性及び受入判定を共通基準へ追加し、同じ統制章をUADC_PoCへ適用する。
- 変更: WORK共通 `AGENTS.md` と UADC_PoC個別 `AGENTS.md`。個別fileの既存固有条件は削除せず、共通章追加に伴い後続章番号だけを繰り下げた。
- 記録: 改訂前版は `docs/Codex/2026/202608/20260816/20260816_0549/agents-governance-harmonization/outputs/backup/` に保存した。
- 検証: UTF-8読込み、見出し順、4個別fileの共通統制章一致、改訂前後SHA-256、禁止語・必須観点、backup一致及びGit/GIT/本番非操作を確認する。
- 状態: WORK文書だけを変更。file削除、GIT側反映、stage、commit、push、外部接続及び本番操作は行っていない。

## 2026-08-16 TEST_RESULTS.md必須化

- テストを1件以上実施した変更作業では、所定task記録の `outputs/TEST_RESULTS.md` を必ず作成する規則を、WORK共通及び4個別 `AGENTS.md` へ追加した。
- 記録にはscope、日時、環境・tool/version、入力・SHA-256、設定、command、期待結果、実結果、PASS／FAIL／SKIP、error／warning、再現性、未実施事項、残存risk及び受入判定を含める。
- テスト未実施時は同fileを必須としないが、未実施理由と影響を完了報告又は本書へ記録する。
- 今回の文書検証結果は `docs/Codex/2026/202608/20260816/20260816_0701/test-results-mandatory-artifact/outputs/TEST_RESULTS.md` に保存する。

## 2026-08-16 変換表仕様書Appendix実使用表inventory

- 正式文書 `Specifications/UADC_Transformation_Table_Specification.docx` の Appendix AへA.5〜A.11を追加した。script-to-table contract、20個の実使用CSV、row数、SHA-256 prefix、header contract及び代表行を収録した。
- 対象scriptは`src/syntax_binding.py`、`src/semantic_binding.py`、`src/syntax_binding_ads_xbrl_gl.py`、retained `csv2tidy.py`／`tidy2csv.py`及び`flat_csv_canonical.py`。将来targetの`semantic_table.py`／`flat_csv.py`は現行実装・table instanceなしと記録した。
- 検証は20/20 CSVの存在・row数・SHA-256一致、DOCX package integrity、A.5〜A.11、25表、追加10表geometry/header repeat/row split禁止及び22/22ページ目視をPASSした。
- 変更前DOCX、CURRENT_BASELINE及びHANDOFFは同taskの`outputs/backup/`へ保存した。`outputs/TEST_RESULTS.md`、`TABLE_INVENTORY.csv`、`CHANGE_REPORT.md`及び`BACKUP_MANIFEST.csv`を証跡とする。
- 既存TOCは明示依頼なしでは更新しないためA.5〜A.11を追加していない。既存表1〜15のlegacy geometryは変更範囲外として維持した。
- 次回開始点: 変換表CSV又はscript loader契約を変更する場合、Appendix inventoryとprogram specificationを同時に更新する。
- code、CSV、private値、file削除、`public/`、GIT、stage、commit、push及び本番操作は行っていない。

## 2026-08-16 Syntax Binding／Flat CSV詳細プログラム仕様書

- 目的: tested Syntax Binding／Flat CSV実装を、codingへ直接接続できる英語の20章詳細仕様書へ展開し、既存Program Specificationも整合させる。
- 成果: 詳細仕様書2件、`Specifications` 改訂2件、candidate copy 2件、Mermaid source 10件を登録した。書式はTaxonomy Framework Part 1をimmutable templateとして使用した。
- 実装境界: Syntax Bindingのforward/reverse object tree・context registry・UBL schema ordering、Flat CSVのcanonical/legacy dispatch・`keyed_rows`・`marker_rows`・source-row/variant identity・reverse conflict aggregationを現行として記載した。`fixed_columns`、atomic publication、structured diagnostic catalog等は未実装／recommendedとして明確に分離した。
- 検証: 既存変換試験と回帰試験PASS、4 DOCXのpackage/20章/framework part preservation/決定性/candidate hash一致PASS、section audit PASS、a11y high 0件。LibreOffice不在でページ画像QAだけSKIP。
- 記録: `docs/Codex/2026/202608/20260816/20260816_1603/uadc-detailed-program-specifications/outputs/` の `TEST_RESULTS.md`、`CHANGE_REPORT.md`、`BACKUP_MANIFEST.csv`、`COPY_PLAN.csv`、各監査JSONを参照する。
- 次回開始点: LibreOffice利用可能環境で4 DOCXをrenderし、ページ切れ、表幅、図caption及び孤立見出しを目視確認する。実装変更時は同じgeneratorとtraceability表を同時更新する。
- 状態: file削除・移動、source code・Binding・HMD・private値・PCA既存文書・`public/`・GIT・stage・commit・push・本番操作なし。

## 2026-08-16 Figure／Table可読性改訂

- 対象: `research/pre-public-validation/` 直下のSyntax Binding／Flat CSV detailed及びProgram Specification 4件。
- 図: 標準10 pt、最小8 ptへ拡大し、boxとspacingも拡張した。Flat CSVへrecommended-onlyの`fixed_columns`図を追加した。
- caption／本文参照: Syntax各文書Figure 4・Table 16、Flat CSV各文書Figure 6・Table 14を連番化し、全番号を本文説明から参照した。
- source: Syntax Mermaid 4件及びFlat CSV Mermaid 6件へ10 pt theme指定を追加した。
- 検証: package、20章、framework部品、caption、本文参照、図サイズ計算、inline image、決定性PASS。a11y high 0件。LibreOffice/soffice不在のためページ画像QAはSKIP。
- 証跡: `docs/Codex/2026/202608/20260816/20260816_0800/figure-table-readability-revision/outputs/`。
- 次の開始点: LibreOffice利用可能環境で4 DOCXをrenderし、特に6.15 inch高のFlat reverse図、caption隣接、table改ページ及び孤立見出しを全ページ目視確認する。
- 状態: full-page visual acceptanceのみ保留。`C:\Users\nobuy\Documents\Codex` 未使用。削除・移動、code、Binding、HMD、private値、`public/`、GIT、stage、commit、push、本番操作なし。

## 2026-08-16 HTD-D入出力詳細説明改訂

- 対象: `research/pre-public-validation/` 直下のSyntax Binding／Flat CSV detailed及びProgram Specification 4件。
- 追加内容: physical input→HTD-D→HTD-CSV及びHTD-CSV→HTD-D→physical outputについて、実装中のobject/list/dict/state、読取・検証・配置・再利用・展開・出力の順序、次元／group identityを英語で詳細化した。
- Syntax固有: `BindingClass` hierarchy、`direct_fields_by_class`、owner-row-first recursion、repeated class ordinal、`context_by_dimension_row[(dimension, ordinal)]`、binding/XSD order。
- Flat CSV固有: `BindingRow`／`GroupSpec`、keyed/marker grouping、`entry_key`／`source_row`／variant identity、`header_values`／`details`、physical column placement、marker regeneration。
- 境界: 共通`HTDData` classを創作せず論理HTD-Dとして記載。CII reverse、`fixed_columns`、atomic publication、manifest等は現行実装と分離した。
- 図表: Syntax Figure 6／Table 19、Flat Figure 8／Table 17。Mermaid source合計14。標準10 pt／最小8 ptを維持。
- 検証: 4 DOCX構造・content・caption・本文参照・framework保存・section・image・a11y high 0・決定性PASS。LibreOffice不在でfull-page renderのみSKIP。
- 証跡: `docs/Codex/2026/202608/20260816/20260816_1215/htd-data-flow-explanation/outputs/`。
- 次の開始点: LibreOffice利用可能環境で4文書を全ページrenderし、追加した4図、caption隣接、table改ページ及び孤立見出しを目視確認する。
- 状態: 削除・移動、runtime code、Binding、HMD、private値、`public/`、GIT、stage、commit、push、本番操作なし。

## 2026-08-16 変換表仕様書Appendix全実データ化

- 目的: Appendixの代表例を廃止し、各scriptが使用する変換表の実データ全体を横長ページへ収録する。
- 実施結果: 20個のCSVについてheaderと全871 data rowをA3横長の独立sectionへ収録した。Table 22〜41の番号・名称を付け、各表の直前にTable番号を参照する説明文とsource metadataを追加した。Appendix BはA4縦へ復帰する。
- 正式成果物: `Specifications/UADC_Transformation_Table_Specification.docx`、SHA-256 `84256241AC887245A4B892B89CD8F5B3599173033DB4A636CC1C4D7ACD6C48AD`。
- 検証: 20/20 CSV、全871行、全cell、空値、順序及びSHA-256一致、22 section、61 Word table、table幅、header repeat、row split禁止、DOCX package、2回生成のSHA-256一致、60/60ページ目視をPASSした。
- 継続規則: WORK共通 `AGENTS.md` に、以降の文書の図中文字10 pt標準・8 pt最小、`Figure n`／`Table n`表題及び本文からの番号参照を追加した。今回追加したAppendixに新規Figureはない。
- 証跡: `docs/Codex/2026/202608/20260816/20260816_0740/transformation-table-full-landscape-appendix/outputs/` の `TEST_RESULTS.md`、`CHANGE_REPORT.md`、`BACKUP_MANIFEST.csv` 及びbackupを参照する。
- 未完了事項／既知の問題: なし。既存TOCは明示依頼がないため更新していない。各表末尾の余白は次表を新しいA3 sectionから開始するための意図した区切りである。
- 次の開始点: 変換表CSV又はscript loader契約を変更した場合、Appendix A.11、program specification及び検証記録を同時更新する。
- 状態: WORK文書と作業記録だけを変更。削除・移動、code、CSV、private値、`public/`、GIT、stage、commit、push及び本番操作なし。

## 2026-08-17 Flat CSV Canonical 17列単一正本化

- 目的: 旧2 entry pointと共通moduleの二重経路を廃止し、Canonical 17列Bindingだけを使用する単一runtimeへ統合する。
- 現行WORK正本: `pre-public-validation/programs/flat-csv/scripts/flat_csv.py`。`to-structured`／`to-flat`、`--hmd-file`、`--binding-file`、`--definition-encoding`、`--profile-width`、物理入出力encoding及び値なしsummaryを実装した。
- 旧13列Bindingは明示エラー・非0終了で拒否する。旧3 programは削除・変更せず履歴比較用に残し、現行正本からimportしない。
- Binding方式: Flat CSV Semantic Path Table、Canonical 17列。PCAは`keyed_rows`、Yayoiは`marker_rows`、両者とも単一`source_rows` driverを使用する。
- 入出力: PCA合成81列2行→Structured CSV→81列2行、Yayoi合成CP932 25列4行→Structured CSV→CP932 25列4行。実会計データは未使用。
- 検証: definition/negative 20件、PCA 1件、Yayoi 1件、匿名81列genericization 1件及びcompileを全件PASS。順逆各2回のbyte決定性、完全往復、PCA Column27競合、Yayoi marker異常、presence及び和暦正逆を確認した。
- 未対応・意味差: tested profileでは値欠落・意味差なし。複数nested header group及び複数独立driverは現行契約外として拒否する。
- README 3件とprofile test 3件を現行CLIへ整合した。test配置は移動・統合していない。
- Word仕様書の正本選択は2026-08-17に解決した。archive／profile candidateを除く最新のProgram、Detailed Program及びTransformation Table正本3点を改訂し、candidate copyは変更していない。
- 証跡: `docs/Codex/2026/202608/20260817/20260817_1708/flat-csv-canonical-unification/outputs/TEST_RESULTS.md`、`reports/GIT_CANDIDATES.csv`、`reports/backup_sha256.csv`。
- GIT・公開・本番: 操作なし。後日GIT候補はfile単位で記録済み。backup、task log、合成生成物、temp、`__pycache__`及びprivate dataは除外する。
- 次の開始点: 後日GIT反映が個別承認された場合、`20260817_1744/flat-csv-canonical-word-specification/outputs/reports/GIT_CANDIDATES.csv`を起点に、正規GIT rootで候補pathの存在と差分を確認してfile単位COPY_PLANを作る。candidate snapshotのrefreshは別承認とする。

## 2026-08-18 設計決定先行4段階再配置

- 目的: 設計決定を先に固定し、WORK全体inventory、Taxonomy dependency、proposed path mapping、Candidate gate、Canonical昇格候補及びGIT差分を`Workbench → Candidate → Canonical WORK → GIT`で整理する。
- 設計決定: `docs/decisions/`へStructured CSV、Flat CSV統合、Taxonomy HMD/Generator再利用のADR 3件を追加し、`docs/DECISIONS.md`へD-031〜D-033を追記した。Structured CSV動的metadata生成は未実装、Flat CSV D-029は維持、Generator/Definition ScriptはXBRL-GL-Next再利用を原則とする。
- inventory: `workbench/migration/UADC_Current_File_Inventory_20260818.csv`に24,327 filesを記録し、SHA-256 error 0。Taxonomy asset inventory、dependency mapping、proposed path mapping、GIT comparison detail/report、findings及びAGENTS追記案も同directoryへ配置した。
- Structured CSV: CSV/JSON pair member 174 filesを同じartifact groupで記録した。JSON metadataは`definitions/`への移動対象にしていない。
- Candidate: `research/pre-public-validation/four-stage-reorganization-20260818/`へFlat CSV runtime、EN-CIUS HMD、XBRL-GL-Next 2 HMD＋manifest、Generatorをcopy-onlyで配置した。source/candidate SHA-256 6/6一致、HMD row/column、manifest 2/2、Python AST 2/2、privacy pattern 0件をPASSした。
- Canonical WORK: ADR 3件、`DECISIONS.md`、本baseline、HANDOFF及びframework directoryだけを変更した。Candidate fileを`definitions/`又は`tools/uadc/`へpromoteしていない。
- conflict: UADC既存GeneratorとXBRL-GL-Next候補のSHA-256が異なるためpromotion停止。ISO-ADC/AICPA-ADS chain、独立Taxonomy Definition Script、外部HMD/EN-CIUS publication terms、dependency path更新はreview-required。
- Flat CSV: `csv2tidy.py`、`tidy2csv.py`、`flat_csv_canonical.py`は変更、削除、移動、legacy化していない。`flat_csv.py`のfull regressionはcode変更なしのため再実行せず、D-029証跡を維持した。
- GIT: 正規rootは`C:/Users/nobuy/GitHub/GIT/UADC-PoC`、branch `main...origin/main`。開始前から`AGENTS.md`に未commit変更があり保持した。read-only比較はgit-only 15、same-path-different 129、same-path-same 615、work-only 23,583。GIT copy、stage、commit、pushなし。
- data/publication: 実会計dataは使用せず、private fileの内容を成果物へ転記していない。inventoryはpath/size/hash/classificationのみ。削除、move、rename、元data上書きなし。
- 証跡: `docs/Codex/2026/202608/20260818/20260818_0631/four-stage-reorganization/outputs/`。
- 次の開始点: (1) Generator conflictの採用版決定、(2) ISO-ADC/AICPA-ADS authoritative chain特定、(3) external HMD/EN-CIUS license判断、(4) dependency path regression計画、(5)明示承認後にCandidate単位でCanonical昇格、の順とする。GIT反映はその後の別承認である。

## 2026-08-20 EN CIUS共通HMD前処理

- 目的: EN CIUS legacy LHMを、family固有形式をGeneratorへ持ち込まず共通前処理でCanonical 18列HMDへ変換し、そこで停止する。
- 実装: `tools/taxonomy/prepare_hmd_for_taxonomy.py`を追加した。入力profileとnamespace modeを別引数とし、single-namespaceでは空`module`、module-basedでは必須`module`を検証する。
- EN CIUS: `specs/lhm/EN16931_CIUS_Invoice_LHM.csv` 197行を変換した。`element` 197/197はprefixなし有効NCNameかつ一意、完全階層は`level + 1`、`lhm_level`はStructured CSV向け圧縮値として不使用、legacy `xpath`はUBL Syntax Bindingとして不使用である。semantic属性4項目の行単位保持は197/197一致した。
- 成果物: `docs/Codex/2026/202608/20260820/20260820_0824/en-cius-common-hmd-preprocessor/outputs/`。Canonical HMDは197行・18列、SHA-256 `0F2687A71031CA2B03C5FCFB2F7200780D4593C1A295DE3A3EDB0D12786BAFA9`。
- 検証: EN CIUS変換、Canonical validation-only、独立2回決定性をPASSした。XBRL GL Next正式Accounting Entries 398行及びBusiness Transactions 433行もmodule-based validation-onlyでPASSし、原本内容は変更していない。
- review-required: ISO ADC／AICPA ADSのauthoritative HMD、module/namespace mapping、`local_name`及びTaxonomy XPath chainは未特定。現行Generatorのsingle-namespace入力契約確認もTaxonomy生成前に必要である。
- 状態: EN CIUS Taxonomy生成、旧Generator削除、consumer改定、ISO ADC／AICPA ADS変換、GIT反映、stage、commit、push、本番・公開操作は未実施。実会計データは使用せず、source LHM/HMDとXBRL GL Next正式HMDは変更していない。
- 次の開始点: review-requiredを解消する別承認後に、Generatorのsingle-namespace受入契約をgeneration logicを変更せず確認する。今回の停止点はEN CIUS Canonical HMD validation PASSである。

## 2026-08-20 EN CIUS共通Generator preflight

- Phase 1で確定したXBRL-GL-Next共通Generator SHA-256 `968D45BCFC244A277C5CF7625A9E0C8746AFF02B3781D9FFD795B922EB724FC4`へ、前工程のEN CIUS Canonical HMDをformal CLIで適用した。
- 絶対パスによる有効なpreflightは、level-1 rootの`module`空欄を`Formal HMD root module/local_name is blank`として拒否しexit 1となった。出力directoryは作成されず、部分Taxonomy 0件である。
- static inspectionではroot identityだけでなく、`gl-<module>:` XPath、GL module namespace、`module:local_name`／`module_local_name`、module別schema/linkbase、package ID及びTuple/OIM entry pointにmodule-based前提が残る。
- Generator、source/Canonical HMD、既存EN Taxonomy、consumer及びXBRL-GL-Next fileは変更していない。Arelle、再現性、candidate/baseline比較は生成前blockのため未実施である。
- consumerは`out/taxonomy/plt/en16931-oim-2026-07-05.xsd`と`en16931:*` conceptを参照するため、formal package layoutとの差を黙示変更できない。
- 証跡とfamily非依存の最小変更案は`docs/Codex/2026/202608/20260820/20260820_0836/en-cius-common-generator-preflight/outputs/`に保存した。
- 次の開始点: authoritative Generatorを置くXBRL-GL-Next WORKの変更承認と、明示的namespace mode／prefix及びentry-point互換方針を確定してから、module-based byte regressionとEN CIUS生成・Arelle・consumer検証へ進む。
## 2026-08-20 EN CIUS module identity / XPath lexical prefix分離

- 指示書 `docs/ChatGPT/2026/202608/20260820/20260820_0921/EN_CIUS_HMD_Module_en16931_XPath_Prefix_en_Codex_Instructions_20260820.md` に従い、`tools/taxonomy/prepare_hmd_for_taxonomy.py`へ一般的な`--module`と`--namespace-prefix`の分離を実装した。EN固有Generatorロジックは追加していない。
- Revised Candidate `docs/Codex/2026/202608/20260820/20260820_0925/en-cius-module-prefix-hmd/outputs/EN16931_CIUS_Invoice_Canonical_HMD.csv` は197行・18列、`module=en16931` 197/197、XPath `en:` 197/197、`gl-en16931:` 0、validation PASS。SHA-256は`E4C43D010BD853A3A70195C6DCB9BE4A4F0EAD6FAD5D1C8825D202BDC538CACA`で、独立再生成も一致した。
- 旧empty-module Candidateとの16非module/non-XPath field比較は差分0。意図した契約差分は`module`と`xpath`のみ。namespace URIは既存`http://www.xbrl.org/int/gl/en16931/2026-07-05`を維持する。
- review-required: 未変更の共通Generatorはformal XPath prefixへ`gl-`を強制するため、`en:`受理には将来の一般的prefix-to-module解決が必要。今回はGenerator変更、Taxonomy生成、consumer変更、ISO ADC/AICPA ADS、Arelle、Git stage/commit/pushを行わず、HMD validation PASSで停止した。
- 詳細証跡は同taskの`TEST_RESULTS.md`、`TASK_REPORT.md`、`VALIDATION_RESULTS.csv`、mapping/design revision及びbackup manifestを参照する。
## 2026-08-20 共通Generator prefix/module分離後のEN CIUS preflight

- XBRL-GL-Next共通Generatorへ一般的な`--namespace-prefix-map PREFIX=MODULE`が追加され、EN CIUS Candidateの`en=en16931`解決はPASSした。`module=en16931`及びnamespace URI `http://www.xbrl.org/int/gl/en16931/2026-07-05`は変更していない。
- EN完全生成の最初の残課題はprefixではなく、semantic datatype `Identifier`が共通Generatorの厳格なdatatype契約に未登録であること。生成はexit 1で停止し、正式EN Taxonomy出力、Arelle、consumer比較は未実施。
- UADC側Canonical HMD SHA-256 `E4C43D010BD853A3A70195C6DCB9BE4A4F0EAD6FAD5D1C8825D202BDC538CACA`は変更していない。次は暗黙推測を避け、既存EN Taxonomyとの型互換を含む一般的datatype対応を別レビューで確定する。
- consumer改定、旧Generator削除、ISO ADC/AICPA ADS、GIT側copy、stage、commit、pushは未実施。

## 2026-08-20 UADC WORK local Git initial baseline

- WORK `C:\Users\nobuy\GitHub\WORK\UADC_PoC`の空／不完全な`.git`を、明示承認に基づきbranch `main`、remoteなしの独立local repositoryとして初期化した。GIT側metadataのcopy及びworktree方式は使用していない。
- initial baselineは`Consumer Migration Phase 1 accepted state`とし、commit subjectは`chore: initialize UADC WORK development baseline`とする。過去状態を人工的に再構成していない。
- baselineには`src/syntax_binding.py`及び`tests/test_syntax_binding_consumer_migration_phase1.py`を含む。Phase 1以前の状態は既存Codex backup/evidenceに保持する。
- `.gitignore`へprivate/raw data、Codex/ChatGPT evidence、generated output、backup、cache/runtime、credential/local configurationの除外を追加した。Candidate/Canonical sourceは一括ignoreしていない。
- initial stageは明示選択289件。private/confidential path、generated/backup/temp path及びcredential pathのstageは各0件である。`out/`、`tests/roundtrip/`、research/workbench、archive、PDF/ZIP/XLSX等はstageしていない。
- WORK commitはdevelopment historyだけを表し、Candidate、Canonical WORK、formal GIT又はGitHubへの昇格承認ではない。GIT側copy・stage・commit・push及びWORK remote/pushは未実施。
- 次の開始点: local WORK履歴を継続する場合もfile単位stageとprivacy検査を維持する。Consumer Migration Phase 2、Candidate/Canonical昇格、formal GIT反映はすべて別承認とする。

## 2026-08-21 handoff: EN CIUS occurrence-key OIM deployment

- The accepted common Generator candidate was deployed to `definitions/taxonomy/en-cius/` and `out/taxonomy/` by replacing only the OIM entry point and dimensional linkbase after non-destructive backup and candidate SHA verification.
- The runtime contract remains `en16931:*` facts/primary items and `plt:d_en16931_*` occurrence dimensions. Dimensions are now limited to the 13 root/repeated Classes; the `ItemAttributes` cube excludes singular `d_en16931_ItemInformation`.
- The current validator, unchanged saved Japan PINT Arelle validation, and task-local 19-case forward/reverse/metadata/semantic regression pass. No source metadata, Structured CSV, roundtrip fixture, private data, formal GIT, stage, commit, or push operation occurred.
- XMLSpy manual confirmation remains `PENDING USER`. Evidence is retained in the XBRL-GL-Next WORK task directory `docs/Codex/2026/202608/20260821/20260821_1119/oim-occurrence-key-generator-revision/outputs/`.

## 2026-08-24 handoff: EN CIUS/gl-btx WORK production release candidate

- Continue from the 216-row HMD, UBL 218-row Binding, CII 222-row Binding, 13-file taxonomy, and 11-row gl-btx Semantic Binding recorded in `docs/CURRENT_BASELINE.md`.
- The production Syntax runtime resolves the flattened model taxonomy layout first and retains the earlier `oim/` layout as fallback; source and model deployment SHA-256 are identical.
- Release validation passed for deterministic taxonomy generation, DTS/package closure, Arelle 2.23.1 Tuple/OIM, synthetic UBL/CII cross-syntax, occurrence-scoped identifier selection, and gl-btx roundtrip.
- Before formal promotion, rerun with Arelle 2.37.77 when available. Separately decide whether to authorize regeneration of `models/en-cius/invoice/fixtures/expected/` and update its relocated test to pass the production HMD explicitly.
- The obsolete `tests/test_xbrlgl_generator_uadc_lhm.py` CLI (`-p`/`-c`) is not evidence for the current Generator and remains a separate maintenance item.
- An old retained test inadvertently accessed PINT JP fixtures; exclude that invocation from acceptance and do not promote its generated outputs. Accepted evidence is synthetic/public and task-local.
- No private accounting data, formal GIT modification, stage, commit, or push occurred.
## 2026-08-24 EN CIUS to gl-btx Semantic Binding coverage expansion candidate

- Authoritative inputs remained unchanged: EN CIUS HMD 216 rows (`19F45D3A...`), gl-btx HMD 403 rows (`48477175...`), and generic `semantic_table.py` (`B5527DB4...`).

## 2026-08-25 Flat CSV Semantic Binding seq/dimension runtime candidate

- `src/semantic_table.py`へ10列v4 Binding、HMD seq/path hard validation、Class Binding、repeatable `d_`ordinal vector伝播、target/source HMD順replay及びselector `[key]`存在判定を汎用実装した。EN、gl-btx又はBT固有の新規条件分岐はない。
- authoritative task inputsはEN CIUS 216-row HMD `19F45D3A...`、gl-btx 477-row candidate HMD `6B8A5C97...`、16-row v3 Binding `A5D7715D...`。v4 candidateは既存16 Attribute行にsource/target seqをmaterializeし、document-root Class Binding 1行を加えた17行、SHA-256 `DDB33ACB9760EFB00948396042BECD1F52206E24F9D4577157488A21357FC1EB`。
- seq/path validation 17/17、必須A〜F 6/6、Identifier／Business Process Type／旧7列contract 5/5、Arelle 2.37.77 2/2がPASS。semantic/value/ordinal diff、cross-link及びcollisionはすべて0。
- 164件は全件再評価したが、seq/ordinal runtimeだけでは未reviewのsemantic／Class対応を確定できないため新規EXACT／TRANSFORMは0。B1=137、B2=10、B3=2、B4=7、B5=8として保持した。
- evidence: `docs/Codex/2026/202608/20260825/20260825_055405/flatcsv-semantic-binding-seq-dimension-runtime/outputs/`。production Binding、relocated model-unit runtime、formal GITは未変更。stage、commit、push、private data、PINT JP fixtureの利用はない。

## 2026-08-25 Semantic Binding HMD-derived repeatable ancestor runtime candidate

- `src/semantic_table.py`は、Attribute Bindingのsource／target `semantic_path`から両HMDのrepeatable ancestor chainを導出し、同数のchainへordinal vectorを位置的に伝播する。明示的なrepeatable Class Bindingは通常処理の必須条件ではない。
- v5 task-local Bindingはv4の17行（Attribute 16、root Class 1）をバイト同一で保持する。seq/path 17/17、Class Bindingなしのsingle／nested repeat、non-repeatable sibling reorder、non-repeatable parent＋repeatable child、count mismatch、missing dimension及びseq/path mismatchの必須検証はPASSした。
- Identifier 7 occurrence、BT-23 Business Process Type、旧7列及びv4 10列contractは回帰なし。semantic/value/ordinal diff、cross-link及びcollisionは0で、Arelle 2.37.77のtask-local OIM metadata 2件はerror 0／warning 0である。
- B1 137件をHMD chainで再評価し、6件はoccurrence mechanism上compatibleだったが、いずれも未reviewのsemantic candidateであるため新規EXACT／TRANSFORMへ昇格していない。164 REVIEW_REQUIREDは維持する。
- evidence: `docs/Codex/2026/202608/20260825/20260825_071314/semantic-binding-hmd-derived-repeatable-ancestor-runtime/outputs/`。production Binding、relocated model-unit runtime、formal GITは未変更。stage、commit、push、private data、PINT JP fixtureの利用はない。

## 2026-08-25 EN CIUS / gl-btx 164-item semantic mapping review

- 残る164 AttributeをEN CIUS／477-row gl-btx HMDのsemantic path、definition、ancestor hierarchy、datatype、multiplicity及び可逆性で164/164再確認した。必要箇所はcurrent gl-btx FSM／BSM／reviewed LHMも参照した。
- 名称類似だけの昇格は0。結果はREVIEW_REQUIRED 158、NO_TARGET 6で、新規EXACT／TRANSFORM／ONE_WAYは0。v6 task-local Bindingはv5の17行をバイト同一で保持する。
- 強い候補にはHeader/Detail Tax、Header/Detail Adjustment、Header Note、Document Attachment、Line/Itemがあるが、TaxType／AdjustmentType／AmountType／ReferencePurposeの承認済みliteral、EE1 role、percentage表現、multiplicity policy、又はselector処理とHMD-derived nested occurrenceの汎用統合が未決定である。
- 新規approved mappingが0のため、新規domain fixture、roundtrip及びArelleは実施せず、条件不変のv5 roundtrip／Arelle証跡を再利用した。production Binding、runtime、HMD/FSM/BSM/LHM、taxonomy及びformal GITは変更していない。
- evidence: `docs/Codex/2026/202608/20260825/20260825_075052/en-cius-glbtx-semantic-mapping-review-164/outputs/`。次工程は共通discriminator／EE1／runtime extension／model extension判断を個別承認し、その後に該当domainだけを再レビューする。
- A task-local 14-row expanded Semantic Binding candidate preserves the accepted 11 rows and adds BT-31, BT-32, and BT-20. The candidate is not production/canonical.
- BT-29/30/31/32 four-kind Seller coexistence and the full 14-row approved-fact roundtrip pass with semantic diff 0; Arelle 2.37.77 reports error 0/warning 0.
- Coverage classifies 216/216 HMD rows: EXACT 13, TRANSFORM 1, REVIEW_REQUIRED 166, NO_TARGET 0, STRUCTURAL 36. Reversible Attribute coverage is 7.78%.
- Line/item, tax, allowance/charge/totals, supporting documents, and additional party roles remain review-required because discriminator, occurrence, multiplicity, or inverse contracts are not uniquely defined. No gl-btx model, EE1 member, runtime, taxonomy, production Binding, or Formal GIT asset was changed.
- Evidence: `docs/Codex/2026/202608/20260824/20260824_175000/en-cius-glbtx-semantic-binding-coverage-expansion/outputs/`.

## 2026-08-24 EN CIUS/gl-btx review-required clustering and v2 candidate

- The 166 previously review-required EN attributes were classified 166/166 into 11 shared design groups; unclassified rows and rows without a shared group are both zero.
- Existing accepted identifier ADR evidence resolves one additional fact: BT-48 Buyer VAT identifier maps through the generic `customer + VAT` Header Identifier Reference contract. No new design value or runtime conditional was introduced.
- The task-local v2 Semantic Binding has 15 rows and preserves the prior 14 rows unchanged. Its SHA-256 is `7E718A6FD4EE1CA8EF4CB97585DB485DA74B44C2EE5C197858B683431C81E7AE`.
- The new BT-48 mapping and seven independent Seller/Buyer identifier occurrences pass semantic/value/occurrence roundtrip diff 0; Arelle 2.37.77 reports error 0/warning 0 for the generated task-local xBRL-CSV metadata.
- Coverage is now EXACT 14, TRANSFORM 1, REVIEW_REQUIRED 165, NO_TARGET 0, STRUCTURAL 36 (15/180 reversible attributes, 8.33%). Remaining resolution states are 157 new-decision, 1 model-extension and 7 EE1-extension required.
- The current runtime only materializes header and Header Identifier Reference occurrence contexts. A future generic, HMD-derived, inverse-defined ancestor-occurrence projection is required before line/item, tax, allowance/charge, document/reference, payment, detailed party/delivery and note mappings can be approved. This architecture was documented but not implemented.
- Production HMDs, runtime, production Semantic Binding, taxonomy and Formal GIT were unchanged. No stage, commit or push occurred. Evidence is in `docs/Codex/2026/202608/20260824/20260824_181500/en-cius-glbtx-review-required-design-resolution/outputs/`.

## 2026-08-27 Canonical CSV UTF-8 no-BOM and Excel bridge handoff

- Canonical project-controlled CSV uses strict UTF-8 without BOM. CRLF and LF record delimiters, quoted-field embedded line breaks, and final-line-break presence are informational when parsing, structure, cell values, and business semantics are preserved.
- Excel review/edit exchange uses `src/csv_excel_bridge.py`; XLSX is not the Canonical source and Excel `Save As` must not overwrite Canonical CSV. The bridge supports `preserve`, `crlf`, and `lf` record-delimiter modes while preserving embedded string newlines.
- The approved scope is 86 CSV files: 71 rebuilt and 15 already compliant. Final validation is 86/86 PASS, BOM remaining 0, and business/semantic difference 0. `JP_LHM.csv` remains unchanged at SHA-256 `34419560590C68CEB22B01BDAB1C124576B944BFB40327759508965664590372`; its 153 quoted-field CRLF occurrences are accepted.
- The previously accepted 45-test bridge result was reused. Only four EOL-preservation delta cases were run, and all passed. No same-input two-run SHA comparison was performed.
- Successor Candidate ID: `en-cius216-gl-btx478-uncl1001-380-ordinal-stable-xbrl-japan-public-csv-utf8-nobom-eol-tolerant-20260827`.
- Candidate path: `.codex/candidate-csv-nobom-eol-0827-ready`; payload 119, promotion rows 202, path/SHA mismatch 0, Candidate CSV BOM 0.
- Self-contained ZIP: `docs/Codex/2026/202608/20260827/20260827_1613/csv-no-bom-work-resumption/outputs/csv-no-bom-eol-tolerant-public-candidate-ready.zip`; isolated extraction validation PASS.
- Formal GIT and publication worktrees remain unchanged. UADC Formal GIT currently has `*.csv text eol=lf`; a separate approved governance change is required before byte-exact placement of CRLF Candidate CSV. Formal GIT placement, stage, commit, and push require separate explicit approval.

## 2026-09-03 UADC Canonical promotion and GitHub publication

- `flat_csv.py`、PCA／EPSON 16-column Semantic Binding及びSyntax／Flat CSV 4仕様書の計7件を、accepted source→Canonical WORK→official GITへbyte-identicalに昇格した。
- official GIT `main`で7パスだけをstageし、commit `2828353d6b4ac91571bae3a043fda488d1c25a0b`（`Promote validated flat CSV bindings and specifications`）を`origin/main`へpushした。HEAD＝origin/main、ahead/behind 0/0。
- PCA Bindingは`local_name` 38/38、fallback 0、EPSONは45/45、fallback 0。PCAの438-row／246-voucher／6,402 comparison、roundtrip、determinism及びArelle結果はexact-byte accepted evidenceを再利用し、重複実行していない。
- EPSON technical publicationはPASS。formal code map、character encoding、actual application importが未完了のためEPSON productionはHOLDを維持する。
- Syntax Binding方式及びFlat CSV 16-column Binding方式を公開対象とした。入力／出力の新規変換は実行せず、実データ値は使用・公開していない。
- Formal GITに作業前から存在した`taxonomy/tuple/btx_businessTransactions/btx-content-2026-12-31.xsd`の未stage変更は、編集、stage、commit、pushしていない。
- private input、EPSON test-only tax map、generated output、backup、log、task evidence及びその他`docs/**`はFormal GIT／GitHubから除外した。
- 全4仕様書のfull-page Visual QAはLibreOffice不在でNOT EXECUTED。Flat CSV 2文書には後続のWord/Poppler fallback visual PASSがあるが、4文書全体のstatusは変更しない。
- 証跡: `docs/Codex/2026/202609/20260903/20260903_1613/uadc-canonical-github-publication/outputs/`。次の開始点は、別タスクでSyntax文書を含む4文書を利用可能なrender環境で全ページ目視確認すること。EPSON production HOLDは別承認・別検証で扱う。

## 2026-09-03 `.codex`／`.chatgpt`日付階層化とテスト結果時刻別登録

- `.codex`直下の76項目及び`.chatgpt`直下の1項目を、名称内の日付、名称内のMMDD（2026年）又は最終更新日の優先順で判定した`YYYYMMDD/`配下へ移動した。移動先衝突0、移動後の非日付直下項目0である。
- 今後の一時作業領域は`.codex/YYYYMMDD/`又は`.chatgpt/YYYYMMDD/`とし、両ルート直下には8桁日付ディレクトリだけを置く。
- 2026-09-03のタスク別正式`outputs/TEST_RESULTS.md` 13件を、それぞれの`docs/Codex/2026/202609/20260903/YYYYMMDD_HHMM/TEST_RESULTS.md`へ同一バイト登録した。日付階層直下の`TEST_RESULTS_INDEX.csv`で元パス、登録先、SHA-256及びサイズを追跡する。
- タスク別テスト証跡は移動・削除せず保持した。テストは再実行しておらず、登録copyのSHA-256一致だけを確認した。
- `docs/CURRENT_BASELINE.md`は正式入力・正式成果物・Git baselineに変更がないため更新していない。Formal GIT、stage、commit、push、公開及び本番操作は行っていない。
- 実会計データを含み得るscratch内容はWORK内の移動だけとし、内容を文書・GIT・公開領域へ転記していない。詳細は`docs/Codex/2026/202609/20260903/20260903_1857/scratch-date-layout-migration/outputs/`を参照する。

## 2026-09-03 PCA→EPSON ordered cumulative pairing candidate

- Task-local successor `.codex/20260903/ordered-cumulative-pairing-20260903_1918/execution_set/flat_csv.py` adds opt-in `ordered_cumulative_pairing`; canonical `tools/uadc/flat_csv.py` remains unchanged pending a separate promotion decision.
- The mode follows original `source_row` order and closes only at positive cumulative debit/credit equality. It materializes 1:1, N:1, 1:N, and exact unique-amount N:M blocks; ambiguous or unclosed blocks fail with classified diagnostics.
- April PCA data generated 437 EPSON detail rows covering 246/246 voucher keys: original-entry shapes 169 1:1, 42 N:1, 2 1:N, and 33 N:M resolved through ordered cumulative blocks. The four formerly excluded vouchers are included.
- Two independent CP932/CRLF/header generations are byte-identical at SHA-256 `4A6380EDB9C7B55725FD519AD1340CC26BE2454615B2341CF4B9DF76887D01F2`. Every row has 45 columns and equal debit/credit amounts; source voucher key set and debit/credit totals are preserved.
- EPSON application import and production code-map validation remain HOLD. No Formal GIT stage, commit, push, or publication was performed; existing outputs were retained.
- Evidence: `docs/Codex/2026/202609/20260903/20260903_1918/ordered-cumulative-pairing/outputs/`.

## 2026-09-03 PCA synthetic pre/post context and GitHub publication

- Implemented a task-local deterministic 16-month generator with two pre-period months, the unchanged 12-month fiscal dataset, and two post-period months. Run1/run2 match for all 10 generated files.
- Pre-period traces derive opening balances for accounts receivable, accounts payable, accrued payables, prepaid expenses, temporary payments, and temporary receipts. Post-period traces reduce all six March 31 closing pools; monthly debit/credit and major-balance nonnegative checks pass.
- Public fiscal input remains 1,271 rows / 708 vouchers / 58 of 58 accounts / JPY 211,762,480 each side. Structured CSV remains 26,339 rows, semantic difference 0, and Arelle 0/0 under reused exact-byte accepted evidence.
- Updated only the English/Japanese original-data READMEs in Canonical WORK to explain the 16-month internal context and 12-month public boundary. The public data files and derived READMEs remain byte-identical to the predecessor.
- Added seven `instances/**/PCA/**` files to Formal GIT and pushed commit `c3f38cf8d4fa43ab860553ac899fda124329971a` to `origin/main`; post-push divergence is 0/0 and all commit blobs match Canonical WORK SHA-256.
- Internal 16-month CSV, masters, opening/closing tables, traces, logs, previews, backups, and task records were excluded from Formal GIT. No real accounting data was used or published.
- The Formal GIT checkout still has the pre-existing unrelated unstaged change `taxonomy/tuple/btx_businessTransactions/btx-content-2026-12-31.xsd`; it was not modified, staged, or committed by this task.
- Evidence: `docs/Codex/2026/202609/20260903/20260903_1933/pca-synthetic-prepost-2months/outputs/`. No production deployment was performed.
## 2026-09-03 Ordered cumulative pairing Canonical review

- Reviewed Candidate `4D246C8B...` against the actual promoted Canonical WORK runtime `tools/uadc/flat_csv.py` (`A59734A...`). The instruction's `pre-public-validation/programs/flat-csv/scripts/flat_csv.py` path is a historical 17-column copy (`1205FE2C...`), not the current promotion authority established by the 20260903_1613 copy plan.
- Generic diff and existing `source_rows`, `balanced_single_counterpart`, and `exact_unique_amount_pairing` regressions PASS. PCA 438-row/246-voucher/6,402-comparison/Arelle evidence was reused without duplicate execution. The 16-column Binding contract remains PCA 38/38 and EPSON 45/45, fallback 0, HMD unresolved 0.
- Canonical promotion is HOLD for three blocking reasons: an empty active-detail entry silently becomes zero rows and is falsely counted 1:1; three of the four newly covered vouchers lose one distinct DetailDescription per side through shared EPSON C38 overwrite; and the accepted specifications do not describe the fourth mode/current algorithm consistently.
- EPSON physical/count result remains 246/246, 437 data rows, 45 columns, CP932/CRLF, deterministic SHA `4A6380ED...`, but previous-HOLD semantic validation is only 1/4 PASS. EPSON Canonical technical gate and production are HOLD; actual application import and formal production code map remain untested.
- No Candidate, Canonical runtime, Binding, HMD, specification DOCX, private source, Formal GIT, stage, commit, push, or publication was changed. `CURRENT_BASELINE.md` and `DECISIONS.md` remain unchanged because no promotion/design adoption occurred.
- Evidence: `docs/Codex/2026/202609/20260903/20260903_1945/ordered-cumulative-canonical-review/outputs/`.

## 2026-09-04 Ordered cumulative pairing semantic-preservation successor

- Task-local Candidate `.codex/20260904/ordered-cumulative-semantic-preservation-fix-20260904_0520/execution_set/flat_csv.py` (SHA-256 `B096D258...`) adds two ordered-mode fail-closed guards: `EMPTY_ACTIVE_SIDE` for an absent active debit/credit side and `MULTIPLE_SEMANTIC_VALUES_FOR_SINGLE_PHYSICAL_TARGET` for distinct values targeting one physical cell. Canonical WORK `tools/uadc/flat_csv.py` remains unchanged at `A59734A...`.
- Four empty/missing-amount cases reject without output or false pairing classification. Previous-HOLD `20210425/253` now passes semantic round-trip and the 45-column/CP932/CRLF/header contract; `20210430/49`, `/70`, and `/137` are explicit safe HOLD with no output and no silent semantic loss.
- Existing `source_rows`, `balanced_single_counterpart`, and `exact_unique_amount_pairing` output and summaries are byte-identical to the predecessor. PCA 438-row/246-voucher/6,402-comparison/Arelle evidence is validly reused. Binding remains 16 columns, PCA 38/38, EPSON 45/45, fallback 0, HMD unresolved 0.
- Task-local Flat CSV Program and Detailed Program Specification Candidate DOCX files add Tables 18–20 for the ordered algorithm, active-side prerequisites, shared-target conflict rule, determinism, and production boundary. Microsoft Word/Poppler render QA passes at 25 and 34 pages; all pages were inspected and caption/table pagination was corrected.
- Canonical promotion recommendation is PASS for the generic fail-closed Candidate, but no promotion was executed. Full April successor output remains unavailable because the file stops safely on a conflict. EPSON actual import and formal production code map remain untested; EPSON production remains HOLD.
- Evidence: `docs/Codex/2026/202609/20260904/20260904_0520/ordered-cumulative-semantic-preservation-fix/outputs/`. Formal GIT, stage, commit, push, and publication were not performed.

## 2026-09-04 Balance-preserving aggregate split pairing successor

- Task-local Candidate `.codex/20260904/balance-preserving-aggregate-split-20260904_0835/execution_set/flat_csv.py` (SHA-256 `86E7A515...`) extends `ordered_cumulative_pairing` with symmetric, unique subset-partition materialization for aggregate/detail splits. Exact unique amounts are resolved first; ambiguous, residual, occupied-row, and complexity cases fail closed with classified diagnostics. Canonical WORK `tools/uadc/flat_csv.py` remains unchanged at `A59734A...`.
- Synthetic 2:1, 3:2, 4:3, 4:2, 5:3, multiple-aggregate, symmetric credit-expanded, ambiguity, blank-row shortage, and residual-mismatch tests pass. Existing four-mode byte/common-summary regressions pass.
- The three prior HOLD vouchers now pass row balance, row-scoped shared-target preservation, identity, totals, 45-column, CP932, CRLF, and reverse-read checks. Full April output covers 246/246 vouchers and 437 data rows; every row and voucher balances, overwrite count is zero, and two runs are byte-identical (`CD0AF7F...`). Private accounting values remain only in WORK scratch and are excluded from task reports, GIT, and publication.
- Task-local Program and Detailed Program Specification Candidate DOCX files describe the implemented algorithm, diagnostics, test evidence, and limitations in Tables 21–23. They retain the Taxonomy Framework-derived style; all 30 tables per document use 100% width, 10 pt text, 3 pt paragraph spacing before/after, 0 top/bottom cell padding, and 1.5 mm left/right padding. Explicit font sizes are integer values with a 9 pt minimum. Word/Poppler full-document visual QA passes at 30 and 38 pages.
- Technical Candidate, specification alignment, and Canonical promotion recommendation are PASS, but promotion was not executed. EPSON production remains HOLD because actual application import and production code-map validation were not executed. `MISSING_REQUIRED_AMOUNT` remains a recommended Binding-contract enhancement because the present 16-column Binding cannot independently distinguish an intentional blank allocation row from a missing active amount.
- Evidence: `docs/Codex/2026/202609/20260904/20260904_0835/balance-preserving-aggregate-split/outputs/`. `CURRENT_BASELINE.md` and `DECISIONS.md` remain unchanged because no Canonical adoption or continuing design decision occurred. Formal GIT, stage, commit, push, publication, and production operations were not performed.

## 2026-09-04 PCA Hyper / EPSON R4 profile review Phase A

- Phase A inventory and mapping-candidate preparation completed with overall status HOLD. Phase B roundtrips were not executed.
- The authoritative April PCA source has 81 columns, 438 data rows, 246 vouchers, and 44 unique account pairs, all matched to the private account reference. Available Hyper and DX samples do not distinguish the source product, and the version/interface identity is unresolved; no profile-specific Binding was created.
- EPSON was limited by user direction to the initial month, 2022-07: 112 of 200 rows and 34 unique account pairs, all matched to the existing reference. Selected mapping status is MAPPED 28, REVIEW_REQUIRED 2, HOLD 3, and EXCLUDE 1.
- EPSON application-family evidence supports 財務会計R4, but the private source has 44 physical columns, mapping metadata states 43 columns, and the current semantic Binding covers 45 columns. Version remains unidentified; no profile-specific Binding was created.
- Six-column account mapping candidates use deterministic collision extensions for one group/four rows in each candidate. EPSON source Category remains blank because it is not evidenced by the available reference.
- Evidence and the mandatory user-review gate are in `docs/Codex/2026/202609/20260904/20260904_1056/pca-hyper-epson-r4-profile-review/outputs/`. Direct test registration is `docs/Codex/2026/202609/20260904/20260904_1056/TEST_RESULTS.md` and is indexed in the date-level `TEST_RESULTS_INDEX.csv`.
- Private raw files were not moved or copied. No `bindings/flat-csv/<profile>/` directory, Canonical promotion, Formal GIT stage/commit/push, publication, or production action was performed. `CURRENT_BASELINE.md` and `DECISIONS.md` remain unchanged.

## 2026-09-04 Reviewed account mapping Phase B roundtrip

- The Phase A review gate was resolved by the reviewed mapping authorities in `docs/ChatGPT/2026/202609/20260904/binding/`. Their exact bytes were adopted into new WORK profile pairs at `bindings/flat-csv/PCA_Accounting_81col/` and `bindings/flat-csv/EPSON_ZaimuKaikeiR4_43col/`; required-field blanks and duplicate source/target codes are zero.
- PCA used the April 81-column source: 438 rows and 246 vouchers. EPSON follows the latest user direction to select the initial month, 2022-07: 112 rows and 78 physical voucher keys. The workbook's first column is management `seq`, so the evidenced R4 application interface is columns B:AR, 43 columns, not the separate 45-column invoice interface.
- Both profiles pass the reviewed-mapping semantic gate: unmapped occurrence 0, ambiguous reverse occurrence 0, Binding-covered semantic difference 0, voucher balance failure 0, shared-value overwrite 0, and byte-identical two-run mapped and reconstructed outputs. PCA has 767 mapped account occurrences including 208 extended-code occurrences; EPSON has 224 including 72 extended-code occurrences.
- NTA `<base>-<suffix>` values are projected as Account Identifier `<base>` and account-subaccount `<suffix>`, then uniquely restored to the original source code/name. The current Canonical converter does not natively consume the six-column mapping, so this integration is a deterministic task-local wrapper and is not a Canonical runtime promotion.
- Physical exact roundtrip remains HOLD. Current Bindings cover 21 PCA and 28 EPSON physical columns; comparison found 5,676 PCA and 901 EPSON non-Binding cell differences. EPSON raw tax codes are retained without an invented production map, and actual EPSON application import was not executed.
- Overall result is HOLD for Canonical promotion while the semantic Phase B result is PASS. No `tests/**` content, Canonical runtime, existing specification DOCX, Formal GIT, stage, commit, push, publication, or production deployment was changed. Private raw copies and roundtrip products remain under `data/private/` and are excluded from publication.
- Evidence: `docs/Codex/2026/202609/20260904/20260904_1241/reviewed-account-mapping-phaseb-roundtrip/outputs/`; direct test registration: `docs/Codex/2026/202609/20260904/20260904_1241/TEST_RESULTS.md`.
## 2026-09-04 Unbound populated cells Excel visual review

- Created a private two-sheet review workbook from the exact Phase B inputs and current WORK profile Bindings. PCA uses `data/private/raw/PCA_Accounting_81col/pca_202104.csv` (438 data rows, 81 columns, two original header rows); EPSON uses the actual Phase B CP932 input for the user-selected initial month 2022-07 (112 rows, 43 interface columns, management `seq` already excluded).
- Binding-derived semantic coverage is 21 PCA columns and 28 EPSON columns. Only nonempty data cells in unbound columns receive light-yellow fill: PCA 5,676 and EPSON 901. Independent source inventory, exported-XLSX OpenXML fill recount, and the Phase B reported counts agree exactly. Bound populated cells and blank unbound cells are not highlighted.
- Source lexical values, source row/column order, original headers, and leading zeros are preserved as text. The workbook contains only `PCA` and `EPSON_R4`, has one AutoFilter table per sheet, no merged cells, and 10 pt body/header text. Five rendered column bands cover all 81/43 columns and pass visual inspection.
- Artifact-tool 2.8.6 did not serialize requested freeze panes after row/column, post-table, and top-row-only attempts. The instruction marks freeze as recommended and does not list it as a mandatory acceptance or stop condition, so this is recorded as a non-blocking limitation; mandatory highlight/value/order/sheet/filter checks remain PASS.
- Five actual highlighted positions per profile are recorded without cell values in `UNBOUND_POPULATED_CELLS_REVIEW.md`. The workbook and column inventory are private review evidence and must not be promoted to Formal GIT or published.
- Evidence: `docs/Codex/2026/202609/20260904/20260904_1324/unbound-populated-cells-excel-visual-review/outputs/`; direct test registration: `docs/Codex/2026/202609/20260904/20260904_1324/TEST_RESULTS.md`.
- Source files, profile Bindings, Canonical runtime, `CURRENT_BASELINE.md`, and `DECISIONS.md` were unchanged. No file was deleted or moved; no Git stage, commit, push, publication, application import, or production operation was performed.

## 2026-09-04 HMD-undefined limitation and Account Mapping runtime integration

- The runtime supports --profile-dir for a same-prefix Binding/Account Mapping pair and --unbound-report for value-free IGNORED_HMD_UNDEFINED reporting. Invalid pairs, duplicate mappings, invalid suffixes, unmapped accounts, and ambiguous reversal fail closed.
- PCA April (438 rows / 246 vouchers) and EPSON 2022-07 (112 rows / 78 vouchers / 43 columns / CP932 / CRLF / header) pass semantic roundtrip, balance, mapping, and determinism gates. HMD-undefined cells are 5,676 and 901 and are accepted known limitations.
- Updated Program/Detailed specifications are registered in Specifications/ and research/pre-public-validation/. Graphviz source is saved with research artifacts.
- Recommendation is YES for separately authorized formal Canonical/Git review. No stage, commit, push, publication, or deployment occurred.
- EPSON production remains HOLD until governed tax mapping and actual application import pass. Evidence: docs/Codex/2026/202609/20260904/20260904_1402/hmd-undefined-limitation-account-mapping-runtime-integration/outputs/.

## 2026-09-07 PCA synthetic opening-balance HMD and Flat CSV Binding candidate

- Created a task-local balance HMD candidate separate from the journal-entry HMD, using ISO 21378 FDIS Table 58 `GL_Accounts_Period_Balance` as the reference model. At the user's direction, Functional/Reporting/Local/Transaction distinctions are not retained: the 20 role-specific source fields are consolidated into `DebitAmount`, `CreditAmount`, `BeginningBalance`, `EndingBalance`, and `CurrencyCode`. Table 58 fields 31–34 (`AccountSegmentEmployee`, `AccountSegmentProject`, `AccountSegmentBankAccount`, and `AccountSegmentX`) are excluded as unnecessary. Field 35 `BusinessSegmentX` is expanded as a Level 2 `BusinessSegment` Composition with the four ISO Table 4 attributes. The HMD has 28 rows; the Coverage table retains all 35 Table 58 source fields, marks fields 31–34 `EXCLUDED_BY_PROFILE`, and marks field 35 `COMPOSITION_EXPANDED`.
- Created a 16-column Flat CSV Binding for all 19 columns of `PCA_SYNTHETIC_OPENING_BALANCES.csv`. Each source row is one account; occurrence selectors expand it into fiscal periods M01–M12. `opening_balance` maps only to M01 beginning balance, month-end columns map to ending balances, fiscal year defaults to 2021, and currency defaults to JPY.
- The source contains 58 synthetic accounts. `flat_csv.py` produced 3,945 Structured CSV data rows and reconstructed 58 source rows. CSV-parser cell comparison is exact; shared-column overwrite, ambiguous reverse mapping, and unmapped account counts are zero.
- The consolidation changed the HMD and Binding, so the new definition received one forward/reverse test. It passed exact CSV-parser cell comparison. With unchanged input, definition, code, configuration, dependency version, and scope, this accepted evidence is to be reused without repeating the test.
- Removing the four unused account-segment rows and expanding the unbound Business Segment Composition did not alter any bound semantic path, the Binding, or existing Structured CSV content. The accepted forward/reverse evidence was reused; after the final added instruction, only the revised HMD/Coverage structure was validated once, with PASS status.
- Table 58 concepts absent from the source remain explicitly unmapped: period debit/credit movements, quantities/UOM, actual beginning/ending balance direction, and account/business segments. `normal_balance` is not substituted for Table 58 fields 17 or 18.
- Overall task-local candidate status is PASS. This is not an ISO conformance decision or Canonical adoption. `CURRENT_BASELINE.md` and `DECISIONS.md` remain unchanged. No Formal GIT, stage, commit, push, publication, application import, or production operation was performed.
- At the user's explicit direction, this task record and its direct test registration were reclassified from `docs/Codex/**` to the corresponding `docs/ChatGPT/**` paths. The move covered 22 files and preserved every SHA-256 and byte count; unrelated `docs/Codex/**` content was not moved.
- Evidence: `docs/ChatGPT/2026/202609/20260907/20260907_0744/pca-opening-balance-hmd-binding/outputs/`; direct test registration: `docs/ChatGPT/2026/202609/20260907/20260907_0744/TEST_RESULTS.md`.

## 2026-09-07 UADC PoC test-file location report package

- Registered `docs/ChatGPT/2026/202609/20260907/20260907_0921/uadc-test-file-location-report/outputs/UADC_POC_TEST_FILE_LOCATION_REPORT.zip`, SHA-256 `9623D3F75E0DC661A5D1F33D088E98A7DE019E6E93308AF22109F34B3CE5BEE8`, 5,034 bytes.
- The ZIP contains exactly three files: a Markdown location report, a 26-row CSV path inventory, and a package SHA-256 manifest. Extracted bytes and hashes match 3/3.
- The report distinguishes private PCA journal data, tax-accountant-supplied EPSON balance/journal originals, public PCA synthetic journal/Structured data, current versus frozen journal HMD references, the task-local balance HMD/Binding, profile Binding/Account Mapping pairs, runtime and test scripts, and the external ISO 21378 FDIS reference path.
- Private source files, the FDIS PDF, HMD/Binding files, scripts, conversion outputs, and backups are not included in the ZIP. Company-identifying EPSON filenames are withheld from the report and inventory.
- No standalone General Ledger, Trial Balance, Balance Sheet, or Profit and Loss artifact was found under WORK; the report records this as a gap and does not equate monthly/opening/closing summaries with those reports.
- No source transformation or prior test was rerun. No Canonical promotion, Formal GIT, stage, commit, push, publication, or external operation was performed.
- Evidence: `docs/ChatGPT/2026/202609/20260907/20260907_0921/uadc-test-file-location-report/outputs/`; direct test registration: `docs/ChatGPT/2026/202609/20260907/20260907_0921/TEST_RESULTS.md`.

## 2026-09-07 ChatGPT client / Codex role governance revision

- Revised the common `C:\Users\nobuy\GitHub\WORK\AGENTS.md` and UADC-specific `AGENTS.md` to distinguish the user, Web ChatGPT, client ChatGPT, and Codex. Roles are assigned per task and are not inferred only from the product or UI name.
- Client ChatGPT is limited to user-authorized paths under `C:\Users\nobuy\GitHub\WORK\`, must not access Formal GIT or GitHub even read-only, and must not follow WORK links outside WORK. Codex remains responsible for authorized implementation, conversion, testing, WORK-to-GIT promotion, and Git/GitHub operations. The user retains final decisions.
- Updated the existing client environment guide as an explanatory document subordinate to the common and project `AGENTS.md`. Added `docs/templates/CODEX_WORK_INSTRUCTION_TEMPLATE.md` with the required purpose, scope, sources, assumptions, work, validation/evidence reuse, Git/publication, deliverables, and handoff sections.
- Original bytes of the common/project AGENTS files, guide, `DECISIONS.md`, `HANDOFF.md`, and date-level test index were backed up before editing with SHA-256 records under `docs/ChatGPT/2026/202609/20260907/20260907_1027/chatgpt-client-agents-role-revision/outputs/backup/`.
- `CURRENT_BASELINE.md` was reviewed and left unchanged because no application, data, HMD, Binding, runtime, Canonical artifact, Formal GIT, or GitHub baseline changed.
- The task used only WORK-side files. Formal GIT and GitHub were not read or modified. No Codex promotion instruction was created because the user did not authorize exact `docs/**` paths for Formal GIT registration.
- Evidence: `docs/ChatGPT/2026/202609/20260907/20260907_1027/chatgpt-client-agents-role-revision/outputs/`.
# 2026-09-07 EPSON参考残高CSVと残高HMD公開

- ユーザー決定により、残高HMD `B4A140F9...3601` のFDIS依存を理由とする公開HOLDは解除済みである。FDIS原本は引き続き除外する。
- 正規モデルは`models/xbrl-gl-next/accounts-period-balances/`へ配置した。HMD/Bindingの技術PASSは`20260907_0744`を`SKIP_ALREADY_PASSED`として再利用し、新しい配置・manifestだけを差分検証する。
- 公開合成データだけから、58科目の2021-04-01開始残高参考CSVと2021年4月試算表参考CSVを作成した。送付候補は`docs/Codex/2026/202609/20260907/20260907_1249/epson-reference-balance-hmd-release/outputs/send-package/`に置く。
- EPSON正式開始残高取込仕様は`UNVERIFIED`、実機取込は`NOT_PERFORMED`である。参考CSVは正式取込対応済みとは扱わず、実際の送付は行っていない。
- Formal GIT/GitHub `main`へcommit `0d54cacfabe7f2519482e30b5e5ec415504a6afd`を通常pushし、remote main到達を確認した。対象外XSDは未stageのまま保護した。

## 2026-09-07 XBRL GL Next Structured Tidy Binding

- The class-occurrence C1...C18 Binding was accepted with LedgerExplorer dataset v3. Structural validation found 23,969 expected/actual facts, missing/extra 0, and Arelle validated all 16 monthly metadata files.
- Task evidence: `docs/Codex/2026/202609/20260907/20260907_192844/structured-tidy-normalization-correction/outputs/`.

## 2026-09-08 Phase 1 Structured Tidy identifier/job contract candidate

- Created a WORK-only successor candidate for April 2021 Accounting Entries and 2021-03-31 balances under `docs/ChatGPT/2026/202609/20260908/20260908_1118/structured-tidy-identifier-job-contract/outputs/phase1-april-contract/`.
- The prior Business Segment extension proposal is withdrawn. The candidate uses existing Accounting Entries HMD classes only: counterparties and departments use separate Detail Identifier Reference occurrences; the project uses Detail Job; Subaccount is limited to account-identifying `account-subaccount`.
- The transaction Structured CSV has 78 rows and C1...C43. It contains 14 Detail Identifier Reference occurrences, one Detail Job occurrence, six account-subaccount occurrences, and zero Business Segment rows. April debit and credit totals remain JPY 1,034,000 each.
- Account codes in the candidate transaction, balance, and expected detail rows use reviewed NTA/e-Tax standard account keys. PCA and former local codes remain trace-only in `ACCOUNT_CODE_MAPPING.csv`.
- C36...C40 now use the complete `C1/C2/C3/C36` hierarchy coordinate and C41...C43 use `C1/C2/C3/C41`; child occurrence numbers are never standalone keys.
- Focused static validation passed 30 checks with zero failures; the added checks cover exact Binding paths, full-coordinate uniqueness, cross-parent child-number reuse, metadata coordinates, and the proposed department exact-pair rule. Two-run generation compared 21 files with zero SHA-256 differences.
- On 2026-09-08 the user adopted same-occurrence `Identifier Type=O AND Identifier Purpose=department` as this candidate's profile rule. It is not an existing standard rule. `O` alone, Purpose from another occurrence, code-prefix inference, and `O` with another Purpose are prohibited. The department-rule HOLD is released; the existing 30 PASS are reused because their prerequisites are unchanged, and only document consistency was checked.
- LedgerExplorer implementation, branch modification, Git operations, and publication were not performed by ChatGPT. Codex implementation remains limited to `structured-tidy-data`; restored main and production must remain unchanged.
- Codex subsequently completed Phase 1 on LedgerExplorer branch commit `427b78eb89b3a0df7b16d2e7bce08a1b3597e4e5`. Git and branch statements are based on Codex evidence under `C:/Users/nobuy/GitHub/WORK/LedgerExplorer/docs/Codex/2026/202609/20260908/20260908_124117/structured-tidy-phase1-contract-gap/outputs/`, not a client ChatGPT live GitHub check.
- The opening-balance description rule is now `開始残高 {科目名}` because the balances source has no invoice/document reference. The two expected-ledger descriptions were corrected and now match the saved generated ledger in all 25 rows and 19 columns. The original expected bytes remain in the 20260908_1456 task backup and Codex comparison evidence.
- Remaining Phase 1 evidence work is limited to five additional view captures and a temporary display-only zero-value fixture. Accounting generation and determinism are not to be rerun. UADC `flat_csv.py` application account/tax-code standardisation remains a separate acceptance item.

## 2026-09-08 Phase 1受入完了とUADCアプリ別コード標準化への引継ぎ

- Phase 1の証跡限定補完を独立照合し、`PHASE1_EVIDENCE_CLOSURE=PASS`として受け入れた。訂正後元帳は25行×19列の論理cell差異0、契約MANIFESTは20/20 SHA一致、既存仕訳＋追加5画面、動的ゼロ表示を確認した。
- 入力契約は`abc-shoten-april-2021-v3`／`abc-shoten-gl-cor-april-v3` 3.0.0、MANIFEST SHA-256 `CEE74D8679534C324767793BC2587961EE27FADE78C6FAE411614F6773FAA2EC`。LedgerExplorer実装commitは`427b78eb89b3a0df7b16d2e7bce08a1b3597e4e5`。
- 詳細は`docs/ChatGPT/2026/202609/20260908/20260908_1644/uadc-app-code-standardization/outputs/PHASE1_ACCEPTANCE_BASELINE.md`及び`INDEPENDENT_REVIEW.md`。Git状態はCodex保存証跡に基づき、クライアントChatGPTはlive確認していない。
- 次作業用に、既存PCA／EPSON Account Mappingを国税庁/e-Tax標準科目キー候補へのレビュー済み内部対応表として参照し、UNCL 5153=`VAT`、UNCL 5305=`S/AA/E/O`、税率`0.10/0.08`へ変換するWORK-only Candidate契約とCodex指示書を同task outputsへ作成した。国税庁公式コード表のsource registerは未確認であり、公式authority PASSとは分けて扱う。
- `TaxTransactionClassification=Sales/Purchase`は既存候補値を保持するが、現行正規Accounting Entries HMDにsemantic pathがない。独自flat列で代替せず、上流モデル・HMD・Bindingを一体で確定するまでこのfactだけHOLDとする。勘定科目、TaxTableCode、TaxCategory及びTaxPercentageRateの実装・検証と分離する。
- CodexはUADC-PoC WORK CandidateとLedgerExplorer `structured-tidy-data` branchだけで作業する。main merge、本番公開、年度12か月、清算16か月及び文書間対応は今回の対象外。
- 次の具体的な一手は`CODEX_START_COMMENT.md`をCodexへ渡し、参照SHA照合後にアプリ別変換・変更範囲試験・LedgerExplorer接続を実施することである。

## 2026-09-08 UADC標準化契約v2限定訂正

- 16:44版契約の国税庁根拠、税率単位、TaxTableCode、EPSON多対一変換及びSales/Purchase候補を再調査し、後継契約を`docs/ChatGPT/2026/202609/20260908/20260908_1743/uadc-standardization-contract-limited-correction/outputs/`へ登録した。16:44版は当時状態の記録として保持し、実装開始には17:43版を使用する。
- 前工程`ACCOUNT_CODE_MAPPING.csv`が使用したe-Tax一般商工業HOT010 BS／PLの絶対path、SHA及び該当行を引き継いだ。国税庁公式ページでファイル名と用途は確認済み。現在WORKでは当時のdownload manifestまで確認できないため、公式ファイル名照合とlocal bytesの取得時同一性を区別する。
- HMD sequence 337の定義文と既存`percentage_to_pure`変換により、TaxPercentageRateは0～1のratioと確定した。10%=0.10、8%=0.08、forward `/100`、reverse/display `*100`とする。
- TaxTableCodeは税務当局の税表コードであり、UNCL 5153 `VAT`を格納しない。Tax Typeは現行Accounting Entries HMDのMODEL_GAP。TaxCategory S/AA/E/OのうちOは明示的対象外だけに使用し、税情報欠損から生成しない。
- EPSONの税込／税抜、元税コード及び元rate字句を変換traceへ保持する。traceによるexact restorationとreverse_priorityによるpolicy regenerationを往復一致として混同しない。
- Sales/Purchaseには2026-09-04の上流FSMから生成されたtask-local候補があり、候補検証はPASS。ただしCanonical未採用のため正式Structured fact出力はHOLDし、重複新設しない。
- 契約静的検証は、初回に旧版由来EPSON SHAの末尾2文字欠落を2件検出し訂正した。訂正後27/27 PASS。検証コマンド記述不備の失敗1回も`TEST_RESULTS.md`へ記録する。Phase 1の会計・帳票試験は再実行していない。
- main、本番公開、Formal GIT及びUADC実装は変更していない。次の具体的な一手は17:43版`CODEX_START_COMMENT.md`を用い、確定済みlookup・補助識別・未対応検出・税率倍率・traceの変更範囲試験を行うことである。

## 2026-09-08 UADC標準化規定v2の限定実装引継ぎ

- 17:43版の内容を引き継ぎ、確定済みの科目対応、`account-subaccount`、UNCL 5305、税率倍率、対象外／欠損、追跡情報及び逆方向判定だけをCodexが先行実装・試験できる後継指示を`docs/ChatGPT/2026/202609/20260908/20260908_1832/uadc-standardization-v2-limited-implementation/outputs/`へ作成した。
- Tax Type及びSales／PurchaseのHOLDは限定試験を止めない。ただし限定範囲PASSと要求全体のHOLDを分け、両項目を欠く出力を完全な標準化済み結果とはしない。
- Sales／Purchaseの9月4日候補は、現行FSMに対するsequence除外後1属性追加と確認した。候補検証は再利用可能だが、Specializationによるgl-btx側派生とCanonical採用差分を確認するまで正式fact出力はHOLDする。
- Tax TypeはAccounting Entries `Detail_ Tax`所有、Token、0..1、UNCL 5153用`Tax_Type`とする未採用案を整理した。TaxTableCode又はgl-btx pathでは代替せず、上流FSMからtaxonomyまでの生成経路を採用単位とする。
- Phase 1の金額・表示PASSは維持するが、旧税率`10/8`のHMD単位適合は引き継がない。新schemaの`0.10/0.08`と画面10%／8%を変更範囲として検証する。
- UADC-PoCはWORK内Candidateだけを対象とし、Formal GIT、GitHub、両main、本番公開及び既存未stage XSDは変更しない。

## 2026-09-08 UADC標準化規定v2 限定Candidate実装結果

- 正規`tools/uadc/flat_csv.py` SHA `94BFC005...F1F59F`を変更せず、`.codex/20260908/uadc-standardization-v2-limited-implementation/`へ隔離Candidateを実装した。Candidate runtime SHAは`2B897F79...2B6952B`。
- reviewed Account Mappingのbase/suffix分離、UNCL 5305 S/AA/E/O、百分率から0..1 ratio、明示O対欠損、source code/rate lexical/税込税抜/D-C/rule/trace SHA、厳密復元とpolicy再生成を実装した。
- PCA 81列とEPSON 43列のFlat→Structured＋trace→Flat実converter往復を含む37 caseがPASS。最終run7/run8の16成果物はbyte一致した。未対応、重複mapping、rate conflict、double scaling、範囲外ratio、trace改変、policy曖昧をfail closedで確認した。
- Phase 1正本のC29だけをtask-localで`10/8`から`0.10/0.08`へ変換し、C29以外の全cell一致、表示projection 10%/8%を確認した。LedgerExplorer runtime接続と画面操作は未実施。5帳票・会計計算・既存表示はcommit`427b78...`のPASSを`SKIP_ALREADY_PASSED`として再利用した。
- Sales/Purchaseの2026-09-04 Candidateは、現行FSM/gl-btx FSM/BSMが当時baselineとbyte一致するため生成証跡を再利用可能。ただしbtxへのSpecialisation波及とvalue rule採用が未決で`HOLD_CANONICAL_ADOPTION`。Tax TypeはAccounting Entries Detail_ Tax、Token、0..1、Tax_Type/UNCL 5153、VAT、FSMからArelleまでの未採用案で`HOLD_MODEL_ADOPTION`。両factはCandidate出力0。
- 判定は限定範囲`PASS_LIMITED_SCOPE`、要求全体`HOLD_REMAINING_MODEL_ITEMS`。Formal GIT、GitHub、両main、本番及び既存未stage XSDは変更していない。commit/pushなし。
- Evidence: `docs/Codex/2026/202609/20260908/20260908_190037/uadc-standardization-v2-limited-implementation/outputs/`。直接登録: `docs/Codex/2026/202609/20260908/20260908_190037/TEST_RESULTS.md`。

## 2026-09-11 V17/V14 V4 Canonical WORK限定反映

- 反映記録は`docs/ChatGPT/2026/202609/20260911/20260911_0754/v17-v14-v4-canonical-limited-promotion/outputs/`にある。変更前byteとSHAは同領域の`backup/`及び`BACKUP_MANIFEST.csv`で復元可能である。
- 既存profileへの波及を避けるため、V4配置計画の既存PCA mapping置換と既存Accounting Entries Binding置換を修正し、明示選択する独立profile／successorへ追加した。
- 使用するFlat CSV結合方式は、81列PCA interface Bindingと74科目mappingのsame-prefix pairである。P0税mapは別の明示引数、同一借貸側属性規則はdataset profile manifestで参照する。
- V14は7列source Bindingから13列Structured Tidy Bindingへ対応する。原借貸額と修正根拠はprivate traceであり、Canonical公開対象には含めない。
- HMDは28行のxpath限定変更で、意味列は不変。既存synthetic profile manifestは新しいHMD SHAへ更新し、意味不変を根拠に既存検証を再利用した。
- 非空取引先の実出現数は0であり、非空値の保存を検証済みとは報告しない。部門・補助・銀行の既存検証とは区別する。
- V17／V14 formal xBRL-CSVはPASS、Canonical promotionはPASS、existing profile impact checkはPASS。Formal GIT、stage、commit、push、GitHub公開はNOT_PERFORMED。

## 2026-09-11 publication dependency resolution handoff

- Use the public candidate at `C:/Users/nobuy/GitHub/WORK/UADC_PoC/.chatgpt/20260911/taxonomy-publication-layout-v5/publication-root/` as the verified copy source. Its required top-level checkout names are `UADC-PoC` and `XBRL_GL_Next`.
- `PUBLICATION_CANDIDATE_MANIFEST.csv` records all 99 source bytes. `MANIFEST_REFERENCE_VERIFICATION.csv` passes 37/37 MODEL/PUBLIC manifest rows; `DTS_REFERENCE_CLOSURE.csv` has no unresolved local reference.
- Monthly metadata 12/12 passes Arelle with 0 errors and 0 warnings. CSV payload files are unchanged; only their metadata taxonomy reference changed.
- XBRL GL Next `origin/main` commit `fe1d9573f86267218dff152ad2e70a4600161e99` already contains the accepted 58-file split taxonomy. Raw WORK/Git archive SHA differences are CRLF versus LF only; LF-normalized content matches 58/58.
- The existing XBRL GL Next Formal worktree is behind `origin/main` and has 58 pre-existing changes. The UADC Formal worktree has one unrelated taxonomy change. Do not overwrite either worktree; a later authorized copy should use a fresh worktree based on the recorded origin commits.
- The copy plan has 38 UADC resources (4 ADD, 17 UPDATE, 17 KEEP). XBRL has 61 resources already present in `origin/main` and one `.gitattributes` UPDATE that fixes `*.xsd`/`*.xml` to LF. No Formal copy, stage, commit, push, or publication occurred in this task.
- Non-empty counterparty occurrence remains zero, so preservation of non-empty counterparty information remains unverified.

## 2026-09-11 Formal GIT publication completed

- The accepted 100-file publication set was audited against the candidate, Canonical WORK where applicable, fresh worktree files, Git index blobs, and commit blobs. All comparisons passed; filesystem and Git-normalized SHA values are recorded separately.
- UADC-PoC commit `f6427e34f3931acabc34aa63891f9c7dec262bf3` was pushed normally to `origin/main`. Actual scope is 4 ADD, 17 UPDATE, 17 KEEP with no deletion.
- XBRL_GL_Next commit `f30297a6148f32ce01a552f0dc3a7eb937f32fc9` was pushed normally to `origin/main`. Actual scope is one `.gitattributes` UPDATE and 61 KEEP resources. The 58 split taxonomy files remained under `taxonomy/accounting-entries` and did not enter the commit diff.
- MODEL/PUBLIC manifest checks passed 37/37; monthly reference resolution passed 12/12; local DTS reference edges resolved 3,033 with zero unresolved; Arelle passed all 12 monthly metadata files and both taxonomy entrypoints with exit 0, errors 0, warnings 0.
- The original Formal checkouts retain the same dirty status sets: UADC-PoC 1 entry and XBRL_GL_Next 58 entries. Their checked-out HEADs remain unchanged.
- Existing synthetic outputs were not regenerated after the V14 HMD xpath-only revision. Non-empty counterparty preservation remains unverified.
- Completion evidence: `docs/Codex/2026/202609/20260911/20260911_0932/formal-git-publication/outputs/COMPLETION_REPORT.md`.

## 2026-09-13 PCA csv2tidy追加登録

- 登録済み汎用生成器: `models/xbrl-gl-next/accounting-entries/scripts/csv2tidy.py`。匿名評価用16列Binding・profile・mapping・taxonomy・テストは`data/private/anonymized/pca-csv2tidy-review-r1/`。旧13列スクリプトと`flat_csv.py`は保持。
- 登録先を使用した8テスト、9,043明細独立照合、Arelle 2.37.77（エラー・警告0）を実施。ZIPの元44,391行CSVにはfact無しルート1行がありArelle非適合だったため、正式CSVからのみ当該行を除き44,390行とした。値・子孫座標は不変。`COPY_PLAN.csv`と再実行ログは`docs/Codex/2026/202609/20260913/20260913_1330/pca-csv2tidy-revision-validation/outputs/`を参照。
- このprofileは内部限定。DatePostedの最終意味判断、取引先・銀行の未Binding、逆変換・他profileは別途レビュー対象。Official GIT/公開は今回未実施。
- 旧model unitの回帰テストは未変更の旧BindingとHMDのsequence相違27行で `SEQUENCE_MISMATCH`、1件ERROR。新経路の登録先PASSとは別の既存経路HOLDとし、旧経路を無断修正しない。失敗ログは同じ証跡領域の`existing_model_tests.log`。

## 2026-09-13 PCA／EPSON Binding契約・仕様書の局所訂正（19:28開始）

- 2026-09-03採用のPCA／EPSON固定順16列Binding定義契約を再確認した。旧17列は`tools/uadc/flat_csv.py`の互換入力であり、新規PCA／EPSON Bindingの正規契約ではない。表は同じプロジェクトの`bindings/semantic/`配下。全profileへの一般化やOfficial GITの配置変更はしない。
- 2026-09-13に明示された別の設計判断は、変換対象の対応付けを`semantic_path`と内包selectorに基づけ、HMDの`id`、`source_bsm_id`、`identifier`による代替照合・補完を行わないこと。11列Structured CSVの`id`出力列は今回変更せず、空欄だけで不具合としない。9月3日の受入へ遡及して記載しない。決定記録は`docs/DECISIONS.md`のD-054を参照。
- `Specifications/UADC_Flat_CSV_Detailed_Program_Specification_2026-08-16.docx`と`Specifications/UADC_Transformation_Table_Specification.docx`を局所訂正した。`Specifications/UADC_Flat_CSV_Program_Specification.docx`は別プロセスの編集ロックが続き、正規WORKへは**未反映**。バックアップから作った訂正候補のみ保管し、ロック解消後に元SHA・差分を再確認してから別途反映する。候補があることを正規仕様の訂正完了と扱わない。
- 変更前byte、候補、変更記録、レンダリング、SHA・差分・完了報告は`docs/ChatGPT/2026/202609/20260913/20260913_1928/official-pca-epson-baseline/outputs/`。`docs/CURRENT_BASELINE.md`は8月17日時点の17列記録と9月3日以降の状態を区別する追記とした。
- 既存のEPSON 4伝票HOLD、43／45列差、諸口999、正式mapping・本番設定・実アプリ取込、年間匿名入力、全旧17列profile互換性は変わらない。変換・再生成・再テスト、AGENTS／実装／Binding／HMD、Official GIT、commit・pushは未実施。

## 2026-09-15 ns20 Canonical WORK受入・公開保留

- ns20候補のpackage READMEを除く94ファイルをCanonical WORKへADD 70、UPDATE 13、KEEP 11で配置し、全destination SHAを候補manifestと照合した。UPDATE 13件の変更前byteはtask-local backupに保存した。
- Arelle 2.37.77の既存PASSは再利用し、正規配置後のSHA・JSON参照・XML closure・6 schema namespaceだけを追加確認してPASSした。Arelleと会計情報保持は別判定で、税額141,601,937円／3,490明細、`TAX_POLICY_AMBIGUOUS`、EPSON実アプリ関連はHOLDのまま。
- Canonical生成器は旧namespaceを再生成するため、上流再発防止はFAIL/HOLD。調査用変更は既存SHAへ復元した。
- `COPY_PLAN.csv`は95件をOfficial GITと比較し、ADD 72、UPDATE 23、KEEP 0。匿名・派生38件とpackage README 1件を除外し、残る56件はnamespace承認順序とD-052 split taxonomyのauthority conflictで保留した。
- Official GITはmainがorigin/mainより1 commit behindで、既存の無関係な未stage変更1件を保持した。copy、stage、commit、pushは未実施。証跡: `docs/Codex/2026/202609/20260915/20260915_0913/ns20-canonical-promotion/outputs/`。
- sibling `GIT/XBRL_GL_Next`はmainがorigin/mainより6 commits behindで、多数の既存stage・unstage・untracked変更がある。ns20には承認済みsplit-path copy mapがないため代替昇格先にせず、同checkoutも変更していない。

## 2026-09-15 Stable module namespace Canonical WORK baseline

- Namespace: `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}` (exact per module; version remains in file names only).
- Accepted semantics: 2026-09-04 tax transaction classification successor with `taxType` VAT/OTH and `entryDatePosted`.
- Active split DTS: Accounting Entries 58 files; Business Transactions 67 files.
- Result: deterministic generation PASS; package closure PASS; Arelle 2.37.77 error 0 / warning 0 for both DTSs and affected samples.
- Evidence: `C:\Users\nobuy\GitHub\WORK\XBRL-GL-Next\docs\Codex\2026\202609\20260915\20260915_1406\stable-namespace-work-unification\outputs\VALIDATION_REPORT.md`.
- External approval is not asserted. Official GIT and GitHub were not changed.

## 2026-09-15 AE/BT root-HMD-specific structural difference acceptance correction

- AE and BT are separately generated hierarchy expansions from different root HMDs. Exact cross-root equality of type, structure, and multiplicity is not required for same-namespace, same-name declarations.
- The tracked 14 differences are classified as `ROOT_HMD_SPECIFIC_STRUCTURAL_DIFFERENCE`; they are not conflicts, defects, or publication holds by themselves.
- Acceptance is based on conformity to each adopted root HMD, complete DTS reference resolution, and Arelle PASS from the corresponding AE or BT Tuple/OIM entry point. Existing 20260915_1406 evidence satisfies these conditions and is reused without rerun.
- The split layout and consumer entry-point selection are mandatory. Same-named files must not overwrite one another, and unconditional DTS mixing is prohibited. Single-DTS combined use is outside scope.
- No HMD commonization or multiplicity relaxation was performed. Namespace remains `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`.
- This decision supersedes descriptions that treated the 14 differences as a conflict or acceptance limitation. Other recorded BLOCKED and unresolved matters remain unchanged.
- Official GIT and GitHub operations were not performed.
