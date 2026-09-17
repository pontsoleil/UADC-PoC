# UADC_PoC Current Baseline
## 2026-09-15 XBRL-GL-Next Tax Type successor baseline

- Canonical UADC now uses the validated XBRL-GL-Next successor based on the 2026-09-04 tax-transaction-classification taxonomy.
- The successor keeps `cor:taxTransactionClassification` (Purchase/Sales) and the distinct `cor:taxType` values VAT/OTH. OTH represents corporate tax and other non-consumption taxes.
- `cor:datePosted` was migrated to the accepted local name `cor:entryDatePosted`; no fact values were deleted or substituted.
- Arelle 2.37.77 validation passed: PCA 130,807 facts and EPSON 134,281 facts, both error 0/warning 0. Canonical WORK promotion verified 25/25 SHA matches.
- Known accounting-preservation issues remain separate: missing EPSON tax-amount facts, `TAX_POLICY_AMBIGUOUS`, and unverified EPSON application import.
- Evidence: `docs/Codex/2026/202609/20260915/20260915_1101/adopt-tax-classification-uadc-alignment/outputs/`.

## 2026-09-07 Accounts Period Balances public model baseline

- Canonical model directory: `models/xbrl-gl-next/accounts-period-balances/`.
- HMD: 28 rows, SHA-256 `B4A140F942E15D1557789239E4D07BC9D888BBE990C56DBA69E2DB9DBAB23601`.
- PCA synthetic opening-balance Binding: 77 rows, SHA-256 `D6F69AFDAA85573247861AA2FA2A6A8463C99703BBDA0ED798E4E733FCAF489C`.
- The user classifies this as an independently designed model that used ISO 21378 as a reference. The FDIS-dependency publication HOLD is released; the FDIS source remains excluded.
- The accepted `20260907_0744` technical result is reused. Publication relocation does not rerun the unchanged 58-row/3,945-row roundtrip.
- EPSON official import compatibility remains unverified and the device import test remains not performed; these are separate from model publication.
- Formal GIT/GitHub `main` publication commit: `0d54cacfabe7f2519482e30b5e5ec415504a6afd`; verified local HEAD = `origin/main` = remote `main`, ahead/behind `0/0`.

## 2026-08-26 formally reviewed CII D16B Syntax Binding/runtime

- Canonical CII Binding: `specs/bindings/syntax/EN16931_CII_D16B_Invoice_Syntax_Binding.csv`, 237 rows, SHA-256 `B529F2585CA2A5FBFDAF673A6F96B98135CE274B8B022C1B791FF9863C23BD23`.
- Canonical generic runtime: `src/syntax_binding.py`, SHA-256 `4D9A163D157C223DCF5FDC68924A08D2BF9CF1AC745AA24D288E57ECF6FF7E3F`.
- Formal source decision: CEN/TS 16931-3-3:2020 Table 2 is authoritative; Table 3 is the inverse/coverage reference; syntax-specific structures remain outside the EN HMD.
- Gate A: 237/237 rows and 13/13 corrections PASS; HMD resolution errors 0; Table 2 deviations 0; Table 3 inverse ambiguities 0; prohibited runtime hard-code 0.
- Accepted predecessor tests were reused because candidate bytes and dependencies were unchanged. Only placement/reference preconditions are rerun after Canonical/Formal placement.
- Evidence: `docs/ChatGPT/2026/202608/20260826/20260826_0957/cii-cen-ts-formal-review-promotion/outputs/`.

## 2026-08-23 Business Transactions Registered Identifier terminology

- `BT05-02` is now `Identification Scheme` / `識別制度`, regenerated from the accepted XBRL-GL-Next FSM CSV through the formal pipeline.
- UADC BT HMD: 403 rows; SHA-256 `4847717501FE9FA2305E9026F75A4FB992490D7228CA2364FEEE60F206ECB93C`.
- The 25-file flattened OIM closure passed deterministic generation, DTS package checking, Arelle 2.37.77 and Structured CSV metadata validation.
- The three-item Semantic Binding subset was not changed and its focused forward/reverse regression remains PASS.
- Evidence: `docs/Codex/2026/202608/20260823/20260823_1552/registered-identifier-identification-scheme/outputs/`.

記録日: 2026-08-20 (JST)

## WORK local Git baseline

- repository: `C:\Users\nobuy\GitHub\WORK\UADC_PoC`
- branch: `main`
- remote: none
- initial baseline subject: `chore: initialize UADC WORK development baseline`
- initial baseline state: `Consumer Migration Phase 1 accepted state`
- initial commit IDは本文書自身を同commitへ含めるため固定記載せず、`git rev-parse HEAD`で確認する。
- `src/syntax_binding.py` SHA-256: `0E264D3048A69BD571CF353D0AB950BB304FE6CA197A7913E1BFF077277FC244`
- `tests/test_syntax_binding_consumer_migration_phase1.py` SHA-256: `C39A8BDBEAF53DC6BC8A525990A49B567DB1CE8427572DE7754950CA92DC2D83`
- WORK commitはdevelopment historyであり、Candidate、Canonical WORK、formal GIT又はGitHubへの昇格承認ではない。

## Formal GIT baseline

- branch: `main`
- upstream: `origin/main`
- code baseline commit: `c504f88dab62a6e6e1248f1fbfa4eaaf169f81ac`
- subject: `Publish reorganized Phase documentation`
- 記録時点のahead/behind: `0/0`
- 本文書を追加するdocumentation commitは自己参照を避けるため固定値として記録しない。最新値は`git rev-parse HEAD`で確認する。

## 正式入力

|相対パス|用途|GIT baseline SHA-256|
|---|---|---|
|`specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv`|UBL Invoice syntax binding|`1C9F629FAE4A36250781EA39418F9817D33436C4FBF9D6E79F30B9ED6A925121`|
|`README.md`|実行経路・文書案内|`6BC4EBBC95515D61E9EEB4CA3B7924B2B3070E34EDD32BAB78D4002F94EA8CA2`|

正式入力は公開sample、外部化されたBinding Table、対応仕様で構成する。実会計データと`README_PRIVATE.md`指定対象は含めない。

## 正式成果物と主要実装

|相対パス|用途|GIT baseline SHA-256|
|---|---|---|
|`src/syntax_binding.py`|Phase 1 syntax binding|`0AF9521C2A0B6A5B418C544DED17A3E4B5CE976FE2846D92A6D75B31029C5CA3`|
|`src/semantic_binding.py`|Phase 2 semantic binding|`1C1CDF42D2EE0E93283BA9D6967876990D9186D35F1B28F0B32AE875D5779C7E`|
|`src/syntax_binding_ads_xbrl_gl.py`|ADS XBRL GL syntax binding|`F0BCE98024C4883B4A2A29334B6E86EA630A117673C6C509DDB4BF6129D778AC`|
|`out/phase1/openpeppol_ubl_invoice_minimal_binding_only.csv`|Phase 1 structured output sample|`89F355C8E91EFDEBC0E33711A73F8158141D534D508F6C61FB07C902F8471070`|
|`tests/test_roundtrip_artifacts.py`|round-trip artifact validation|`592FC0320D6917D7E55E3BDD1965738EEA706A7D47B988A430FD0AEE7D2AF173`|

成果物の主な配置:

- `out/phase1/`: Phase 1生成例
- `out/taxonomy/`: local生成taxonomy
- `tests/roundtrip/`: review可能なround-trip fixture
- `docs/`: Phase別仕様・tutorial

## WORK正本（Canonical Flat CSV仕様書、2026-08-17）

> この節の「正本」「現行」とSHAは**2026-08-17時点の17列方式の履歴**を表す。現在のPCA／EPSONのBinding定義契約や現在のWORK文書SHAを示すものではない。後続の2026-09-03 Canonical・GitHub publication baselineおよび2026-09-13のD-054を参照する。旧行・旧SHAは来歴として保持する。

|相対パス|用途|WORK SHA-256|
|---|---|---|
|`research/pre-public-validation/UADC_Flat_CSV_Program_Specification.docx`|Canonical 17列Flat CSV Program Specification正本|`0A985CE4A2E22384307D2C8195BD6F82493CC6BA5E01FC27B44E2446D5D3126D`|
|`research/pre-public-validation/UADC_Flat_CSV_Detailed_Program_Specification_2026-08-16.docx`|Canonical 17列Flat CSV Detailed Program Specification正本|`D9078086DF784544724AC32D7211B105E6B889A30B167E743AECBAADB250AD01`|
|`Specifications/UADC_Transformation_Table_Specification.docx`|Transformation Table Specification正本|`0AF8CF0E6B79FF54AAADA8CA339F21CB3674FD0AC9229A17C5F9881896180631`|

- 同名系列では、archive及びprofile candidate snapshotを除く最新更新版を2026-08-17の改訂元として選択した。
- 3文書は`pre-public-validation/programs/flat-csv/scripts/flat_csv.py`、Canonical 17列Binding、`to-structured`／`to-flat`及び現行検証結果へ整合済みである。
- 旧実行スクリプトの解説、比較表、dispatch図及び旧関数一覧は正本から除外した。13列Binding拒否は現行エラー契約としてのみ記載する。
- 2回の独立DOCX生成SHA-256一致、ZIP再読込、目次field、section、style/theme/numbering/settings、図表連番、旧実行名0件を確認した。LibreOffice不在のためページ画像renderは未実施である。
- 実会計データは開かず、既存の合成試験結果だけを仕様へ反映した。GIT、GitHub、public及び本番は変更していない。

## 検証状態とWORK差分

- baseline commitの追跡ファイル数: 702
- 記録作業では変換・round-tripテストを再実行していない。
- WORKとGITでBinding CSV及び代表Phase 1 outputは一致する。
- WORKのREADME、主要3実装、round-trip testはGIT baselineと異なる。WORKを新しい正本としてGITへ反映する判断は本作業の対象外であり、別途差分レビューが必要である。
- WORK直下は2026-08-20に独立local Git repositoryとして初期化した。branchは`main`、remoteは設定していない。上記formal GIT baselineは別repositoryの2026-08-14記録値であり、WORK履歴と混同しない。

## WORKファイル配置目録

- 配置: `research/shared-resources/manifests/UADC_PoC_full_file_inventory_20260815.xlsx`
- SHA-256: `C41243397721A1A1B8B5254D80CA103F1FB80B085E216C8DA17FB5F8BA5BDA12`
- 対象: WORK 21,551件、別管理GIT側スナップショット1,629件
- 比較: same 653件、different 93件、WORK-only 20,805件、GIT-only 883件
- Research Move Plan: 21,442件。全件`inventory-only; not approved to move`
- 公開状態: 全既存成果物は`research-unreviewed`、公開成果物0件
- 状態: WORK側の調査・移動計画用成果物であり、Git baselineを変更するものではない。既存ファイルの移動、名称変更、削除は未実施である。

## WORKレビュー定義（PCA Accounting Entries）

- 配置: `docs/ChatGPT/2026/202608/20260814/20260814_1932/pca-xbrl-gl-next-subaccount-binding/outputs/`
- 対象: PCA GL Flat CSVからXBRL GL Next Accounting EntriesへのSemantic Binding
- EntryDetail: `EntryDetail[cor_DebitCreditIndicator="D"]`と`EntryDetail[cor_DebitCreditIndicator="C"]`の2種類
- Subaccount: 通常の`Subaccount`、`Subaccount[cor_Type="department"]`、`Subaccount[cor_Type="partner"]`。`cor_Type="sub-account"`は使用しない。
- `selector`列: 18列スキーマ互換のため保持するが、条件は`semantic_path`へ一元化し全行空欄とする。
- 検証: UADC 18列契約、全41行、Group Definition Row 11、PCA物理列30、mapped 24、extension-required 6、unmapped 0、固定値行0、HMD未解決0
- 状態: WORK側のレビュー成果物であり、上記Git baselineを変更するものではない。GIT/GitHubへの反映はCodex担当の別作業とする。

## WORKテスト拡張（PINT Japan UBL Invoice）

- 入力: `samples/input/pint-jp-examples/`のUBL Invoice 9件
- 取得元: `pint-jp-resources-dev (11).zip`内`trn-invoice/example/`
- 取得元ZIP SHA-256: `2D0BB36C14106649F8C14C3E2377C0BD027FB434BD908AFEB06900EE620AA570`
- 入力プロファイル: `CustomizationID=urn:peppol:pint:billing-1@jp-1`、`ProfileID=urn:peppol:bis:billing`
- Binding: `specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv`
- forward: 9/9 PASS、各177列・4～20階層行
- source UBL 2.1 schema: 9/9 PASS
- round-trip構造確認: 全データセット19/19 PASS
- reverse UBL 2.1 schema: PINT Japan 9/9 PASS。全データセット19/19 PASS
- forward決定性: CSV/metadata 18ファイルの2回実行SHA-256不一致0件
- Binding Table: 199行すべてにXSD由来`syntax_sequence`を設定。`mimeCode`及び`NetworkID`のsyntax-only `NA`既定値行を含む
- 条件付き既定値検証: 添付7件、CardAccount 1件で`NA`を補完し、親構造がないケースでは新規作成しないことを確認
- selector検証: 19件の逆変換で`ChargeIndicator` 38値が`true`又は`false`として生成された
- 未実施: PINT base及びJapan jurisdiction Schematron
- 状態: WORK側のテスト拡張であり、上記Git baseline、`public/`及びGIT/GitHubは変更していない。

## WORKテスト拡張（UN/CEFACT CII 100.D16B）

- Schema: CrossIndustryInvoice `100.D16B` SCRDM Subset、uncoupled/decoupled-code-list branch、XSD 54件
- 配置: `out/cache/CII-D16B-SCRDM-Subset/uncoupled-clm/CII/`
- 固定取得元commit: ConnectingEurope/eInvoicing-EN16931 `b6c9e06a59812fb1a83585da40923b3678a649ad`
- 公開入力: `samples/input/cii-d16b-examples/`の3件。原本変更及び派生入力なし
- Binding: `specs/bindings/syntax/EN16931_CII_D16B_Invoice_Syntax_Binding.csv`、34行、HMD未解決0、XSD構文順未解決0
- HMD: `specs/lhm/EN16931_CIUS_Invoice_LHM.csv`、SHA-256 `3209C1A2C12BF602A87865162814969486A63958BEBF00F62253005D64279DFE`
- XSD参照: 54/54 PASS、欠落import/include 0
- 入力XSD検証: 3/3 PASS
- forward: 3/3 PASS。明細は5・20・3件、ヘッダー税内訳は3・2・2件、Structured CSVは9・23・6行
- `CII_example6.xml`: 税内訳2件を別`dVatBreakdown`行へ入力順に出力し、各行の課税対象額・区分・税率・税額の所属を保持
- 決定性: CSV 3件及びmetadata 3件の2回実行SHA-256不一致0件
- 回帰: 既存UBL/PINT Syntax Bindingテスト7件PASS、逆変換UBL schema 19/19 PASS
- 未完了: CII日付ISO正規化、CII reverse、EN 16931 CII Schematron、34行範囲外の項目、candidate snapshot更新
- 状態: WORK側のDevelopment Draft。`public/`、GIT側、stage、commit、pushは変更していない。

## XBRL GL Next Accounting Entries HMDのpre-public参照配置

- 最新正本は`C:/Users/nobuy/GitHub/WORK/XBRL-GL-Next/semantic-model/LHM_for_taxonomy/`のHMD 2件と`manifest.csv`の3ファイルセットとする。
- 3件を`research/pre-public-validation/pca-xbrl-gl-next-flat-csv-binding/source-references/`へコピーした。Accounting Entriesは18列・398データ行、Business Transactionsは18列・433データ行である。
- `semantic_path`、`associated_module`＋`local_name`、XPathの重複はいずれも0件。manifestの出力行数及びSHA-256と一致する。
- SHA-256はAccounting Entries `0730006AAA1F84C9E14F1347BF134F40A02A9F0B660A34849F465F57C8509E2A`、Business Transactions `49D54DF6536E37C3911650535E33F55AC5F6FA6E3ED620D6AC355E8ED318BE01`、manifest `9F940D302AFE041CFF3299258A6A28A0EF5077230546F8F554099CC7DC93C605`である。
- 以前コピーしたXLSX、Journal Entry抽出版及び旧Bindingは削除せず、historical development referenceとして残す。最新版HMDの代用にはしない。
- `public/`、GIT側、stage、commit、pushは変更していない。

## PCA Flat CSV 38行レビュー表の最新HMD整合

- ChatGPT指摘対象の旧40行表を履歴として保持し、最新398行Accounting Entries HMDに基づく38行改訂版を`research/pre-public-validation/pca-xbrl-gl-next-flat-csv-binding/source-references/`へCSV/XLSXで追加した。
- selector除去後のHMD解決は38/38件、ID・level・type・datatype・multiplicity整合は全件PASSである。
- HMDの現行IDへ更新し、`cor_DetailSubaccount`を`cor_Subaccount`へ、補助科目profile値を`auxiliary-account`へ改訂した。
- PCA税区分名をXBRL GL Next `Tax Description`へ結合していた2行は意味不一致のため除外した。税区分名は未結合とし、拡張又は税区分マスターによるenrichmentの対象とする。
- Flat CSV仕様は`[n]`と`[condition]`の両selector、HMD照合時の除去、親key＋group_key＋predicateによるoccurrence identity、predicate値の列／`default_value`供給及び`PATH_SELECTOR_VALUE_MISSING`を明記した。
- このレビュー時点では、正規変換スクリプト名を`csv2tidy.py`と`tidy2csv.py`と確認したが、private版は旧13列Binding契約だけであり、17列改訂表によるforward/reverse/round-tripは未実施だった。後続の「WORK実装baseline」で解消済み。
- 改訂CSVの決定性、canonicalized XLSXの決定性及びSpreadsheet目視QAはPASS。DOCXは構造QA PASSだが、LibreOffice不在のためページ画像QAは未実施である。
- 実会計データ、ファイル移動・削除、`public/`、GIT側、stage、commit、pushは操作していない。

## PCA Flat CSV物理列一意化と旧スクリプト解釈

- `csv2tidy.py`及び`tidy2csv.py`は固定13フィールドを位置で割り当て、Bindingを`column`だけをキーとする辞書へ格納する。重複`column`はfan-outされず後勝ちで上書きされる。
- 現行legacy表を実際に読み込むと、`csv2tidy.py`は87 Binding key・81物理列で重複3行を上書きし、`tidy2csv.py`は`semSort`あり32行だけを保持して26物理列を出力対象とする。
- 最新のshared-detail表は37行・17列とし、非空`column`はPCA headerless 81列profileの`ColumnN` 20件で全件一意である。レビュー表示は物理Column順を基本とし、Tax CategoryとAmount of Taxesは連続配置する。`sequence`は最新版HMDの値をそのまま使用する。出力はoccurrence groupを先にまとめ（PCAはD→C）、各group内をsequence昇順とし、D/C横断の単純sortは行わない。XMLスキーマ順はこの表では扱わない。
- PCAに物理Line Number列がないためLine Number Bindingを除外し、各入力行からD/C Detailを各1件作る`source_rows`を追加した。借方Detailを唯一のreverse driver、貸方Detailを同一source-row ordinalのpaired groupとした。
- 元CSVにEntryDetail列はないため、EntryDetailは`column`空欄の共通`source_rows`テンプレート1行とし、selector付きの科目、部門／補助科目、税、金額及びD/C Indicatorだけを借方／貸方へ分ける。
- 共通摘要`Column27`は共通テンプレートへ一度だけ定義する。forwardではD/Cへ継承し、reverseの複数非空値は後処理値で上書きしてエラーにせず、終了時ログに物理columnと件数だけを集計する。値及び行別警告は記録しない。
- 37/37行の最新HMD解決、20/20物理列一意性、税項目連続表示、Spreadsheet目視QA及びcanonicalized XLSXはPASS。DOCX構造QAはPASS、LibreOffice不在によりページ画像QAは未実施である。
- この調査時点の旧スクリプトは現行17列、最新HMD path、`source_rows`及び完全81列reverseを実装していなかったため、変換・往復テストは未実施だった。後続の「WORK実装baseline」でcanonical経路を追加し解消済み。
- 実会計データ、ファイル移動・削除、`public/`、GIT側、stage、commit、pushは操作していない。

## WORK実装baseline（PCA Flat CSV canonical 17列変換）

- 実装日: 2026-08-15
- Binding方式: Flat CSV Semantic Path Table（17列）。正式表は`research/pre-public-validation/pca-xbrl-gl-next-flat-csv-binding/source-references/PCA_GL_XBRL_GL_Next_Flat_CSV_Table_shared_detail_20260815.csv`、37行、HMD解決37/37、非空物理列20/20一意。
- HMD: `research/pre-public-validation/pca-xbrl-gl-next-flat-csv-binding/source-references/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv`。
- 実装: `private/legacy_sources/accounting/programs/flat_csv_canonical.py`を共通処理として追加し、`csv2tidy.py`及び`tidy2csv.py`から17列headerの完全一致時だけdispatchする。旧13列経路は維持する。
- 入出力: headerless PCA 81列合成CSV 2行 -> canonical tidy 75行 -> headerless PCA 81列2行。
- 検証: forward PASS、reverse PASS、81列完全往復PASS、D→C occurrence順PASS、各occurrence内HMD sequence順PASS、forward/reverse各2回決定性PASS、Column27後値上書き・完了時集計PASS、legacy reader dispatch/count回帰PASS。
- 実データ利用: なし。private PCA入力は開いていない。
- SHA-256: `csv2tidy.py` `79669FFE1BFE0118855869564BFECCC53BF514DE4425E78DA8D50B2A701E3550`、`tidy2csv.py` `B8673BD2A5D2DB6D10914E277D8AB6C37348F5B349D89A55C561DCC52FBBC416`、`flat_csv_canonical.py` `5759EA748EE411E28321061BF35F1A9799529D208F06AE0257C812E97B155C68`。
- 合成往復source/reverse SHA-256: `74c59bdf4541422f787a1480c49680d92ae494cfcbd565c5edf5d624de565c25`。forward SHA-256: `e18482fadeb3bdcb65fc16b2b39104ef2948712cacf632268bab3a5bcdde09d2`。
- 仕様書: Transformation `20E155D0ABC456E65B317615FD93C0184EA158F93B2D361913EC575D9CD2C833`、Flat CSV Program `1FEA3554FED34C52DCE9BE1C0C41FBA695858021F6908407E030E8FAEA752AF2`。pre-public candidateコピーとSHA一致。
- 状態: WORK/private及びpre-public Development Draftだけを変更。`public/`、GIT側、stage、commit、pushは未操作。

## WORK現行baseline（Generic Journal Entry Flat CSV）

- 更新日: 2026-08-15
- package: `research/pre-public-validation/generic-journal-entry-flat-csv/`。
- profile: `anonymized-accounting-csv-81`。製品固有名を使用しないheaderless 81列の匿名profileとする。
- 過去版: 旧ベンダー名付きpackage、28行／38行表、20260814資料、archive、過去作業記録及び旧生成物は変更せず対象外とした。
- backup: `docs/Codex/2026/202608/20260815/20260815_1828/generic-journal-entry-anonymization/outputs/backup/`。36ファイル、SHA-256不一致0件。対応表は同outputsの`BACKUP_MANIFEST.csv`。
- Binding: `source-references/Generic_Journal_Entry_XBRL_GL_Next_Flat_CSV_Table_20260815.csv`及び`.xlsx`。37行、17列、HMD解決37/37、非空物理列20/20一意。
- 匿名81列profileの現行ファイル名、text、DOCX/XLSX内部XMLに対する旧PCA固有名scan: 0件。後続で明示名のYayoi 25列profileを別profileとして追加しており、この0件は同profile名を対象としない。
- genericization: `flat_csv_canonical.py`はEntryHeader物理keyを`group_key` JSONから取得し、driver variant値と処理順をBindingのselector宣言から取得する。Column2及びD/Cをprogramへ固定しない。
- profile test: D→C、81列2行、forward 75行、reverse 2行、完全往復、各方向2回決定性及びColumn27集計overwriteがPASS。
- genericization test: `group_key=Column3`及びvariant `LEFT/RIGHT`の派生Bindingでprogram変更なしの完全往復PASS。
- SHA-256: Binding CSV `DFADA7D007B43044CD5CED60A0285F1C0022B1CC5DCC5E92F88A4D8743685CBD`、XLSX `AA61B65EC951AF20BC5FDBDC1C39BF61F89D83A79EED666BD178831E7967F01A`、`flat_csv_canonical.py` `EF7A32421F26187C4E2BFAE808571351F85BE5E9EC934AA322E9BC1C7DDFE7C9`。
- 仕様書SHA-256: Transformation `8E0CF6A9299FCD238926E0471426C0DBB1947E876073FD5D5DC96426AC3E2364`、Flat CSV Program `68D2610B9502379733B7B39463E8A75F56F34305E50906D9CB0AE79CF1AA0413`。
- 状態: WORK及びpre-public Development Draftだけを変更。実会計データ、`public/`、GIT側、stage、commit、push、本番は未操作。

## WORK追加profile（Yayoi Blue Return Journal 25-column）

- 更新日: 2026-08-15
- 配置: `research/pre-public-validation/generic-journal-entry-flat-csv/profiles/yayoi-blue-return-journal-25/`。
- Binding方式: canonical 17-column Flat CSV Semantic Binding。35データ行、最新版Accounting Entries HMD解決35/35、非空semantic column 16件一意、Column1はsemantic値ではなく`marker_rows`制御列。
- 入力profile: headerless 25列、物理CSV CP932、Binding/HMD/tidy UTF-8。複合仕訳はBinding内2000/2110/2100/2101規則で復元する。
- genericization: `marker_rows`、`row_role=presence`、optional Class suppression、bidirectional `jp_era_date_to_iso`、物理／定義encoding分離を実装した。
- 合成試験: 単一仕訳1件及び3行複合仕訳1件のforward/reverse、25列完全往復、決定性、片側variant、任意group抑制、異常marker拒否PASS。
- private実入力検証: 244物理行、244仕訳group、D/C occurrence各244、行単位貸借不一致0、forward決定性PASS、Binding対象列＋marker制御列reverse一致PASS。
- 全物理列完全往復は未達。未結合のColumn20/23/24/25に各244非空値、計976 cellを`unbound-source-control-fields` lossと分類した。値は記録していない。
- SHA-256: Binding CSV `EBFE16173FD25BF987871B7AFA5DDE3B78E9AC4866AE032939E26758615C2796`、XLSX `ADCF0D907CCBA18961D5644C4BBFC9C69462F4F140DAFF05483779D8A850A923`、`flat_csv_canonical.py` `A20D96F209F154CF9820102813DFCE55D213A601E79B7D58D7923D524EA85340`。
- entry points SHA-256: `csv2tidy.py` `082B5185FE7F28BD91F8987AB04F7055A220AEA5D9B4F892A6D63F723C490FA1`、`tidy2csv.py` `49174CF0483FEE727FB1921F6330907947FB463DDB34782B7EBC6017AC62E6AB`。
- 仕様書SHA-256: Transformation `DD13F96AF7BE0C06D9D0E753566DD33B78964FA3C06369E28F5811F4F70EE5D9`、Flat CSV Program `E8BBA1F75B5A8720CEE449B88B0727F9D1FB5D6303A7E5EEFF01969C8C299ECA`。candidate copiesと一致。
- 状態: 実入力、実変換結果、詳細reportは`private/`のみ。原本変更、ファイル削除、`public/`、GIT、stage、commit、push、本番操作なし。WORK自体がGit repositoryでないため追跡状態はGitで確認不能。

## 2026-08-16 AGENTS.md運用統制baseline

- WORK共通 `AGENTS.md` SHA-256: `649475023BC0226FAC8BE7835CD588B24212EAA1320C3B91370EC90D7418322A`
- UADC_PoC個別 `AGENTS.md` SHA-256: `C62FA3FF08E25835CE11EB1F26A9924B5B110B27D131ABFE512441B96D108864`
- 4プロジェクト共通の個別章として、開始前確認、変更範囲、禁止事項、安全策、成果物・log・記録、backup・復旧、失敗時対応、test、再現性、受入判定、Git運用及び終了checkpointを固定した。
- WORK側既存fileの削除は実対象の個別指定がない限り禁止し、WORK変更、GIT反映、stage、commit、push、外部接続及び本番操作を別承認とする。
- 今回は運用文書だけを変更し、code、正式model/data、公開成果物、GIT側、本番baselineは変更していない。
- テストを1件以上実施する変更作業では、所定task記録の `outputs/TEST_RESULTS.md` を必須成果物とする。

## 2026-08-16 Transformation Table Specification Appendix inventory

- `Specifications/UADC_Transformation_Table_Specification.docx` の Appendix A に A.5〜A.11を追加し、現行scriptと変換表の対応、実使用CSV、loader-visible header及び代表行を記録した。
- inventoryは20ファイル（Syntax Binding 2、target-view semantic binding 10、ADS XBRL GL binding 6、canonical Flat CSV compatibility binding 2）。各CSVのdata row数とSHA-256 prefixを本文へ、full SHA-256をtask記録へ保存した。
- 改訂後DOCXは22ページ、25表、SHA-256 `BD22F78744D498C6E291ADACDCBE6BD49DD8AA0754C09FCB5AB9A0023D41580A`。追加10表は固定幅、header repeat、row page-split禁止を満たす。
- 完全CSVを正本とし、Appendixはruntime inventoryである。当時未実装とした`flat_csv.py`記述は、2026-08-17のCanonical単一runtime実装及びWord仕様書改訂で置き換えた。`semantic_table.py`は引き続き未実装である。
- 既存TOCは明示依頼なしでは更新しない規則に従い変更していない。code、CSV、private値、`public/`、GIT、stage、commit、push及び本番は変更していない。

## 2026-08-16 Syntax Binding／Flat CSV詳細プログラム仕様書

- 英語の詳細仕様書2件を `research/pre-public-validation` の現行Syntax Binding及びGeneric Journal Entry Flat CSV candidateへ登録し、`Specifications` の既存2文書とcandidate copyも同一実装baselineへ改訂した。
- 20章構成で、実引数、正確な入出力、class/object/list/dict/state/function、分岐、hierarchy、occurrence、診断、直接write、test traceability及び制約を記載した。
- `keyed_rows` と `marker_rows` は現行実装、`fixed_columns` は未実装のrecommended enhancementとして分離した。structured diagnostics、atomic publication、rollback、manifest、hash publicationは現行動作として記載していない。
- 書式はTaxonomy Framework Part 1を基準とし、styles、theme、numbering、settings、font table、footer、A4 geometry及び表現規則を保持した。Mermaid sourceはSyntax 4件、Flat CSV 6件をcandidate配下へ保存した。
- 構造・書式・決定性検証はPASS。accessibilityはhigh 0件で、1-cell code exampleを通常表として検出するmedium findingだけを記録した。LibreOffice不在のためページ画像QAはSKIP。
- SHA-256: Syntax detailed `3D6F8D77F4D07AC8F5D48983A271256FCF7BE92B1551452CA1D54D99DBF9A1D5`、Flat detailed `3A7333D4EC0B0D063A700EE989532C7637D21F3A54C323A74B24F959600AEB46`、Specifications Syntax `B4630DD2DCA3930DABA3350B3C6B3C1A56BCBB061D4064D05887965350473A36`、Specifications Flat `F8C22E3585971DAA18F439E74A03BE0CE9502190D632B87BFD177C7B57F22755`。
- file削除・移動、source code・Binding・HMD・private値・PCA既存文書・`public/`・GIT・stage・commit・push・本番操作は行っていない。

## 2026-08-16 Figure／Table可読性改訂

- ユーザーが `research/pre-public-validation/` 直下へcopyした4 DOCXを正式な改訂対象とした。nested candidate及び `Specifications/` のcopyはこの改訂では再生成していない。
- 図中文字はWord配置幅6.349206349 inchに対して標準10 pt、最小8 ptとし、8 pt未満を使用しない。Mermaid source 10件も10 pt指定へ更新した。
- Syntax文書はFigure 4件・Table 16件、Flat CSV文書はFigure 6件・Table 14件。全件へ番号と表題を付け、本文中に同じ番号を参照する説明文を追加した。
- SHA-256: Syntax detailed `9175BABB0CC523DBB7CA75BFE7DAA3D8542508A3246B002AA3DFDEF3AA24B0E6`、Flat detailed `9FDCCAD9DF2848E78126E84E46061E512138A79CA52FBE40F4AE8A26BB877CA8`、Syntax Program `BD6EC11EEA03A4B9EFF880581DC6B4D0BFD0E083649FDCABAA1959A703374C17`、Flat Program `E2D7150CB3F330A4E624CD11A84832A66E691AF7B22FB4796C7AE829DC762C43`。
- 構造、caption、本文参照、framework package部品、決定性及び画像監査はPASS。LibreOffice不在のためDOCXページ画像QAはSKIPし、full-page visual acceptanceは保留。
- `C:\Users\nobuy\Documents\Codex` は使用していない。file削除・移動、code・Binding・HMD・private値・`public/`・GIT・stage・commit・push・本番操作なし。

## 2026-08-16 HTD-D入出力詳細説明改訂

- `research/pre-public-validation/` 直下のSyntax Binding／Flat CSV detailed及びProgram Specification 4件へ、物理入力→HTD-D→HTD-CSVとHTD-CSV→HTD-D→物理出力の保持構造、読取順、位置付け、階層／group identity、展開順及び出力処理を追加した。
- HTD-Dは実装に存在しない共通classとして創作せず、Syntax Bindingでは`BindingClass` tree、row辞書、dimension ordinal及びXML element context、Flat CSVでは`BindingRow`／`GroupSpec`、record辞書、`entry_key`／`source_row`／`occurrence`の組合せとして説明した。
- XMLの階層・QName・次元ordinal方式と、Flat CSVの物理列・keyed/marker group・source row/variant方式の対応順序の違いを比較表と本文で明示した。
- 図表はSyntax各文書Figure 6／Table 19、Flat CSV各文書Figure 8／Table 17。新規Mermaid 4件を加え、sourceは合計14件。図中文字は標準10 pt、最小8 ptを維持した。
- SHA-256: Syntax detailed `566688A03DE815461C9FB0EF4629A3727D5C5D23657F113A26466D03D2F0C847`、Flat detailed `398307645CB49D228E8BEBA93CCEA6CBACEEED9877E6576DED16D09D7FE34EC0`、Syntax Program `C0AF60C4352E1EF191D467AF39AB20A94A9EF63A0CE9625DF436DFC30CE1E864`、Flat Program `24AB14ADC4920B9A186C50D3CCC33FDFB7AD2E09B8932ABC5EAC9D4F32EDB18C`。
- 構造、content、caption、本文参照、framework部品、section、image、a11y high 0及び決定性はPASS。LibreOffice不在のためfull-page renderはSKIP。
- 証跡: `docs/Codex/2026/202608/20260816/20260816_1215/htd-data-flow-explanation/outputs/`。削除・移動、code、Binding、HMD、private値、`public/`、GIT、stage、commit、push、本番操作なし。

## 2026-08-16 Transformation Table Specification full-data landscape appendix

- 正式文書: `Specifications/UADC_Transformation_Table_Specification.docx`。
- Appendix A.11は代表行から、現行20個の実使用変換表CSVの全header・全871 data row・全cellへ置換した。列順、行順、空cell及び値をCSVどおり保持する。
- 各実データ表はA3横長の独立sectionとし、前後はA4縦へ戻す。実データ表はTable 22〜41で、各表の直前に同じTable番号を参照する説明文、source path、row／column数及びSHA-256を置く。
- 改訂後DOCXは60ページ、22 section、Word table 61件、SHA-256 `84256241AC887245A4B892B89CD8F5B3599173033DB4A636CC1C4D7ACD6C48AD`。
- 20/20 CSVの全cell一致、DOCX package、section geometry、caption、本文参照、決定性及び60/60ページ目視をPASSした。既存TOCは明示依頼がないため更新していない。
- WORK共通 `AGENTS.md` に、以降の文書について図中文字10 pt標準・8 pt最小、Figure／Table連番表題及び本文番号参照を必須とする共通規則を追加した。
- code、CSV、private値、file削除、`public/`、GIT、stage、commit、push及び本番操作は行っていない。

## 2026-08-17 WORK実装baseline（Flat CSV Canonical 17列単一正本）

- 現行WORK正本は`pre-public-validation/programs/flat-csv/scripts/flat_csv.py`である。`to-structured`及び`to-flat`の2サブコマンドを持ち、Canonical 17列Bindingだけを受理する。
- 旧13列Bindingは`UNSUPPORTED_LEGACY_BINDING`として非0終了で拒否し、旧処理への自動fallbackは行わない。
- `csv2tidy.py`、`tidy2csv.py`及び`flat_csv_canonical.py`はprivateの履歴・比較用資産として変更せず保持し、現行正本からimportしない。
- 正本SHA-256: `0EC0AB9DF4AE78FA5EE8CF678807C014D5101374C94AC558BA318FF96F566E33`。共通定義検証test SHA-256: `15CFC2534A27F7BAC04D69EFB2B6705FC0B9A8FE9EB46DCC3B79B7DA917F2A5E`。
- PCA合成81列2行はforward/reverse各2回一致、完全往復、D→C、HMD sequence順、通常競合0件及びColumn27競合1件をPASSした。
- Yayoi Blue Return合成25列・CP932 4行は2伝票group、forward/reverse各2回一致、完全往復、和暦正逆変換、presence抑止及びmarker異常拒否をPASSした。
- 共通定義・negative 20件、PCA 1件、Yayoi 1件、匿名81列genericization 1件、Python compile及び静的検索をPASSした。実会計データは開いていない。
- 証跡: `docs/Codex/2026/202608/20260817/20260817_1708/flat-csv-canonical-unification/outputs/`。backup 16件はSHA-256不一致0件である。
- Word仕様書の正本選択はユーザー指示により解決済みである。archive／profile candidateを除く最新3点へCLI、Canonical-only validation及び自動fallback廃止を反映し、本書上部の「WORK正本（Canonical Flat CSV仕様書、2026-08-17）」へSHA-256と検証状態を記録した。
- WORK側だけを変更し、file削除・移動、`public/`、GIT側copy、stage、commit、push及び本番操作は行っていない。

## 2026-08-18 4段階artifact lifecycle設計・調査baseline

- lifecycleは`Workbench → Candidate → Canonical WORK → GIT`とし、再配置前にStructured CSV、Flat CSV、Taxonomy再利用のADR 3件及び`docs/DECISIONS.md` D-031〜D-033を記録した。
- Structured CSVは同一data/test case directoryのCSV＋instance別JSON metadataのlogical pairとする。動的列・metadata生成とconsistency validationはFuture Extensionであり未実装である。
- Flat CSVはD-029の`pre-public-validation/programs/flat-csv/scripts/flat_csv.py`を現行WORK実装正本として維持し、4段階配置上はCanonical path昇格待ちCandidateとする。旧3 scriptは変更・削除・移動していない。
- inventory snapshotは24,327 files、SHA-256 error 0、duplicate hash group 1,109、Structured CSV pair member 174 files。成果物は`workbench/migration/`に配置した。
- Candidate packageは`research/pre-public-validation/four-stage-reorganization-20260818/`。6 source assetsのcopy integrity、HMD contract、manifest、Python AST、privacy patternを検証したが、全件promotion HOLDである。
- UADC Generator `B6168D37FE634572222CA88E9E50AA5DC485EAE06AD74192600DB7A29BA2D8E3`とXBRL-GL-Next候補`205FD43B730993C573ED55228FA4E01BE490A17CC1177EACDD9A995E2AA05447`は異なるため、Canonical target overwriteを停止した。
- ISO-ADC及びAICPA-ADSの完全なHMD→Definition Script→Generator→Generated Taxonomy chainは未特定。XBRL-GL-NextはGenerator CLIを直接使用し、独立したfamily別Taxonomy Definition Scriptは確認できなかった。
- 新規framework directoryは作成したが、`definitions/`及び`tools/uadc/`へfileを昇格していない。GIT側はread-only比較のみで、既存`AGENTS.md`変更を保持し、stage、commit、pushを行っていない。

## 2026-08-21 EN CIUS occurrence-key OIM taxonomy baseline

- Canonical snapshot and runtime deployment now use occurrence-key dimensions only. The OIM entry point SHA-256 is `3FB7F9B07FE0916D0454DC0F30F26CFC55769E78E378352EA108019D1AAB1716`; the dimensional linkbase SHA-256 is `0DF545E4AF2DA2F41A8A34BA6EAFE330B7670D862FE44424F66B0CEDBD3A132F`.
- All 33 Classes retain hypercubes and primary items, while the 13 root/repeated Classes define occurrence dimensions. `ItemInformation [1..1]` has no dimension; `ItemAttributes` has exactly `dInvoice`, `dInvoiceLine`, and `dItemAttributes`.
- Canonical validator passes with closure 7, hypercubes 33, dimensions 13, primary items 33, and facts 164. Arelle 2.37.77 validates the unchanged saved Japan PINT xBRL with error 0/warning 0; EN roundtrip regression passes 19/19 with semantic differences 0.
- Source HMD, metadata, Structured CSV, and saved XBRL are unchanged. Formal GIT, stage, commit, and push were not performed.

## 2026-08-24 EN CIUS 216-row / gl-btx WORK production baseline

- `models/en-cius/invoice/hmd/EN16931_CIUS_Invoice_Canonical_HMD.csv` is the WORK production HMD: 216 rows, 18 columns, SHA-256 `19F45D3A108EFF3412A935B2C053CE056E79EC7B28CE1485AAFF8741BE5F3D78`.
- Production Syntax Bindings are UBL 218 rows (`0AD5197F001D281D0EA425E2FAFD66DCFCFFC314247BD41032F2F2E4C776A4F8`) and CII D16B 222 rows (`C1BA0A94523E808D29D88366CA8B0180EEC9CE371BE6AAFAC4D7D30CEAA69DE8`).
- The production 13-file EN taxonomy is deterministic and DTS-complete. Seller Identifier, Buyer Identifier, and Item Classification Identifier occurrence dimensions are present; package failures are 0.
- UBL/CII roundtrip and cross-syntax comparisons pass for scheme-bearing repeatable identifiers and identifiers without schemes. CIUS/gl-btx identifier regression passes without kind confusion.
- Arelle 2.23.1 validates Tuple/OIM and representative OIM instances with error 0/warning 0. Arelle 2.37.77 revalidation remains pending.
- The old model-unit expected Structured CSV pair remains on the former 197-row contract and is not part of this promotion; separate maintenance authorization is required.
- Evidence: `docs/Codex/2026/202608/20260824/20260824_151828/en-cius-production-promotion-release-validation/outputs/`.
- Formal GIT, stage, commit, and push were not performed.

## 2026-09-03 Flat CSV／Binding／仕様書 Canonical・GitHub publication baseline

- PCA／EPSONの固定順16列Binding定義契約は、この2026-09-03受入・公開で採用された事項であり、2026-09-13に再確認した。旧17列は公開変換器の互換入力で、PCA／EPSONの新規作成・受入契約ではない。他profileの互換性・受入へ一般化しない。9月3日の公開コピー元には旧17列専用の仕様本文が残っていたため、実装・Bindingの採用と当時の公開仕様書本文の一致を区別する。
- 2026-09-13に**新たに明示された**D-054の判断は、PCA／EPSON Flat CSV変換を`semantic_path`と内包selectorで対応付け、HMDの`id`による照合・補完・代替解決を行わないこと。`source_bsm_id`／`identifier`も変換用`id`の代用としない。Structured CSVの`id`出力列は今回不変であり、空欄だけを変換不具合としない。これは9月3日の技術受入へ遡及させない。
- 本件の正規WORK仕様書の局所訂正、バックアップ、変更前後SHA、文書検査は`docs/ChatGPT/2026/202609/20260913/20260913_1928/official-pca-epson-baseline/outputs/`に記録する。Official GITへの仕様訂正反映は今回行わない。

- Accepted source 7件をCanonical WORKへ昇格し、同一相対pathでofficial GITへ反映した。Canonical pathは`tools/uadc/flat_csv.py`、`bindings/semantic/PCA_Cn_SEMANTIC_PATH_BINDING.csv`、`bindings/semantic/EPSON_Cn_SEMANTIC_PATH_BINDING.csv`及び`Specifications/`の4仕様書である。
- SHA-256: runtime `A59734A167AED36DA06CA95BEE18C4FC3A1BF37881C8F1FB13C9D644132EFBFF`、PCA `2EC0822C0471EFABD3D4BEA3D0C2FA23521B893009D4134C72FA0A4441DB3E27`、EPSON `6A21ADE0F79A1D83BB6C99F5C66D6C2E12E3CADABF44A0B54876748DC235CB04`。
- 仕様書SHA-256: Syntax detailed `566688A03DE815461C9FB0EF4629A3727D5C5D23657F113A26466D03D2F0C847`、Syntax Program `294A5D3B7B079278285C807FB0C22F8F687874A8AA2D4F17B7B266BAE1FCB1D1`、Flat detailed `D9078086DF784544724AC32D7211B105E6B889A30B167E743AECBAADB250AD01`、Flat Program `0A985CE4A2E22384307D2C8195BD6F82493CC6BA5E01FC27B44E2446D5D3126D`。
- PCA accepted baselineは438 source rows、246 vouchers、6,402 semantic comparisons、difference 0、roundtrip／determinism PASS、Arelle 2.37.77 error／warning 0/0、unknown concepts／unmapped 0/0。EPSON Binding technical promotionはPASS、productionはHOLDを維持する。
- Formal GIT `main` commitは`2828353d6b4ac91571bae3a043fda488d1c25a0b`、remoteは`https://github.com/pontsoleil/UADC-PoC.git`。push後HEAD＝origin/main、ahead/behind 0/0である。
- accepted source＝Canonical WORK＝official GIT＝origin/mainのSHA identityは7/7 PASS。既存の未stage taxonomy差分は今回のcommitへ含めていない。
- 全4仕様書のfull-page Visual QAはLibreOffice不在によりNOT EXECUTEDで、publication instructionによりCanonical gateを妨げない。task evidenceは`docs/Codex/2026/202609/20260903/20260903_1613/uadc-canonical-github-publication/outputs/`。

## 2026-09-03 PCA Synthetic Annual Demo public baseline

- Public PCA input is `instances/original/PCA/PCA_synthetic_annual_demo.csv`: 1,271 fiscal rows, 708 vouchers, 81 columns, SHA-256 `874909A8AE812DFE7B26A73AAD34C1B9381C3403506071566BEDCAB5B4A463A0`.
- Public Structured CSV is `instances/derived/PCA/PCA_synthetic_annual_demo_structured.csv`: 26,339 rows, SHA-256 `FD9C87A7F0CB8B5B436E6DB80527697438E8A1D1857EF77B8E1767D53F480769`; metadata SHA-256 is `4F0BFA9B971E9A586947862769B3B71EE1E92F79A0487987099B5747A44A7701`.
- The synthetic scenario is generated across two pre-period, 12 fiscal, and two post-period months. Only the fiscal 12 months are public. Internal context totals 1,379 rows / 816 vouchers and balances at JPY 272,179,230 debit and credit.
- Opening balances for six open-item accounts are pre-period-derived; remaining opening items are scenario-designed or balancing equity. Opening assets and liabilities plus equity both equal JPY 62,484,810. Six fiscal closing pools have validated April/May settlement traces.
- Canonical PCA Binding remains 16 columns, local_name 38 / 38, fallback 0, unresolved 0. Public semantic roundtrip remains difference 0; Arelle remains 0 errors / 0 warnings through unchanged accepted bytes.
- Formal GIT/GitHub `main` baseline is commit `c3f38cf8d4fa43ab860553ac899fda124329971a` (`Add PCA synthetic annual demo`), with HEAD = origin/main and ahead/behind 0/0.
- Evidence: `docs/Codex/2026/202609/20260903/20260903_1933/pca-synthetic-prepost-2months/outputs/`.

## 2026-09-04 Reviewed account mapping Phase B WORK profile baseline

- WORK profile pairs are `bindings/flat-csv/PCA_Accounting_81col/` and `bindings/flat-csv/EPSON_ZaimuKaikeiR4_43col/`. Each directory contains one interface Binding and one reviewed six-column Account Mapping. The mapping columns are exactly `Account_Code`, `Account_Name`, `Category`, `eTax_Account_Code`, `eTax_Account_Name`, and `Note`.
- A reviewed NTA code of `<base>-<suffix>` is represented as Account Identifier `<base>` plus account-subaccount `<suffix>` during the semantic projection. Reverse projection uses the reviewed mapping only when the mapping is unique; unmapped and ambiguous cases fail the Phase B acceptance check.
- PCA April validation used 438 source rows and 246 vouchers. EPSON validation follows the user's initial-month selection and used 2022-07: 112 source rows and 78 physical vouchers. Both profiles have unmapped account occurrence 0, ambiguous reverse mapping 0, Binding-covered semantic difference 0, voucher balance failure 0, shared-value overwrite 0, and deterministic mapped/reconstructed output.
- The EPSON source worksheet has 44 columns including management `seq`; the application interface is the remaining 43 columns. The derived R4 profile therefore excludes `seq`, excludes invoice-system columns that belong to the separate 45-column interface, and serializes 43 columns with header, CP932, and CRLF. Raw tax category values are preserved because a governed production tax-code mapping was not evidenced.
- Full physical exact reconstruction remains HOLD: 5,676 PCA cells and 901 EPSON cells outside the current Binding are not reproduced. The six-column Account Mapping integration is implemented only by a task-local projection wrapper; `tools/uadc/flat_csv.py` was not changed. EPSON application import and governed tax-code validation were not executed.
- Overall Canonical adoption is HOLD. Formal GIT/GitHub, stage, commit, push, publication, and production deployment were not changed. Evidence: `docs/Codex/2026/202609/20260904/20260904_1241/reviewed-account-mapping-phaseb-roundtrip/outputs/`.

## 2026-09-04 HMD-undefined limitation and Account Mapping runtime integration baseline

- HMD-undefined populated physical cells are a known limitation, not a semantic roundtrip defect. Conversion uses IGNORE + REPORT without cell values; HTD-D, sidecar JSON, and passthrough retention are not used. PCA 5,676 and EPSON 901 cells no longer block Canonical promotion.
- tools/uadc/flat_csv.py now loads an exact same-prefix Binding/Account Mapping pair from bindings/flat-csv/<profile>/. The six-column authority ends in eTax_Category; mapping data is not hard-coded.
- PCA April passes with 438 rows and 246 vouchers. EPSON initial month 2022-07 passes with 112 rows, 78 vouchers, 43 columns, header, CP932, and CRLF. Both have zero semantic differences, unmapped accounts, ambiguous reversals, and voucher imbalances, and both are deterministic.
- The two Flat CSV Word specifications and research/pre-public-validation copies are aligned and pass structural/full-page visual QA.
- Canonical promotion recommendation is YES. Formal GIT stage, commit, push, and GitHub publication were not performed. EPSON production remains HOLD for governed tax mapping and actual application import.
- Evidence: docs/Codex/2026/202609/20260904/20260904_1402/hmd-undefined-limitation-account-mapping-runtime-integration/outputs/.

## 2026-09-07 XBRL GL Next Accounting Entries Structured Tidy Binding baseline

- Canonical Binding: `bindings/structured-csv/XBRL_GL_Next_AccountingEntries_Cn/XBRL_GL_Next_AccountingEntries_Cn_BINDING.csv`.
- Schema v2 uses C1...C18 class-occurrence rows and resolves to the canonical HMD SHA-256 `DEB79F98462AE073BE7CD1102C73427CF8630203F7B872B82DB23A8D1909E46C`.

## 2026-09-08 LedgerExplorer Phase 1受入済みbranch baseline

- Phase 1入力契約はdataset `abc-shoten-april-2021-v3`、Accounting Entries schema `abc-shoten-gl-cor-april-v3` version `3.0.0`である。契約MANIFEST SHA-256は`CEE74D8679534C324767793BC2587961EE27FADE78C6FAE411614F6773FAA2EC`。
- LedgerExplorer実装は`structured-tidy-data` branch commit `427b78eb89b3a0df7b16d2e7bce08a1b3597e4e5`で受入済み。main `574eb6484b84c60785bf3dcad5e52a100a1aac46`及び本番は未変更。Git状態はWORK内Codex証跡に基づく。
- 期待結果SHA-256は水平仕訳`1132FA4A...C75C`、元帳`A1C114F1...169E0`、試算表`A67F9073...01E`、BS`CD423F17...29F5`、PL`ED969C58...9A6`。証跡限定補完はPASS。
- 詳細引継ぎ基準は`docs/ChatGPT/2026/202609/20260908/20260908_1644/uadc-app-code-standardization/outputs/PHASE1_ACCEPTANCE_BASELINE.md`。
- 次のCandidateはPCA／EPSONの国税庁/e-Tax標準科目候補及びUNCL 5153/5305税標準化である。既存Account Mappingはレビュー済み内部対応表であり、国税庁公式コード表とのauthority照合は未完了として分離する。UADC Formal GIT、LedgerExplorer main及び本番公開は未承認・未変更。

## 2026-09-11 V17/V14 V4 Canonical WORK限定反映 baseline

- V4 evidence ZIP SHA-256 `D338AE695E3B439A0A11886327DC1410C5B6CE8D02AF688BD87F5A1903D48655`を反映元とし、承認対象だけをCanonical WORKへ限定配置した。
- 匿名datasetは`config/datasets/anonymous-evaluation-v17-v14.json`と`config/profiles/anonymous-evaluation-v17-v14.json`を明示選択する。entityはscheme `http://www.example.com`、identifier `ABC-SHOTEN`であり、共通defaultではなくfallbackを禁止する。
- PCA 74科目mapping、P0及び同一借貸側属性規則は`PCA_Accounting_81col_AnonymousEvaluation_V17_V14`専用profileへ配置した。既存`PCA_Accounting_81col`は変更していない。
- V17 C1-C35 Bindingは`XBRL_GL_Next_AccountingEntries_C35` successorとして追加し、既存`XBRL_GL_Next_AccountingEntries_Cn`を変更していない。V14 7列入力Bindingも既存19列Bindingから分離した。
- V14 Accounts Period Balances HMDは28データ行の`xpath`だけをQNameへ整合した。`semantic_path`、`associated_module`、`local_name`、`class_term`は変更していない。
- V17 44,391 Structured Tidy行／186,092 facts、V14 37科目／75構造行／292 facts／借貸各336,674,556円及び期間条件は、V4とのSHA対応と限定影響検証で維持した。
- Formal GIT、commit、push、GitHub公開は実施していない。候補及びCanonical WORK内の匿名評価資源は`INTERNAL_USE_ONLY / NOT_FOR_PUBLICATION`である。

## 2026-09-11 PCA synthetic xBRL-CSV publication dependency baseline

- Monthly metadata 12 files now resolve the accepted Accounting Entries split successor from sibling checkout `XBRL_GL_Next`; the relative reference is `../../../../../XBRL_GL_Next/taxonomy/accounting-entries/oim/cor_accountingEntries/cor-all-oim-2026-12-31.xsd` from each `structured/YYYY-MM.json`.
- The independent publication layout contains sibling `UADC-PoC` and `XBRL_GL_Next` roots, 99 public files, no task-local absolute paths, and no anonymous V17/V14 profile markers. DTS local references resolve 3,425/3,425.
- Arelle 2.37.77 validates all 12 monthly xBRL-CSV metadata files and both Tuple/OIM taxonomy entrypoints with exit 0, errors 0, warnings 0.
- The accepted 58-file taxonomy is reproduced twice by the canonical XBRL GL Next generator with zero byte differences from WORK Canonical. Compared with the legacy flat Formal checkout, 12 files are identical, 6 are namespace-only, and 40 contain substantive successor changes; the split root must not be collapsed into the legacy tree.
- XBRL GL Next WORK Canonical now includes a limited `.gitattributes` policy fixing generated `*.xsd` and `*.xml` to LF. A task-local clone with `core.autocrlf=true` preserves the OIM entrypoint SHA exactly; no taxonomy content changed.
- Existing synthetic outputs were not regenerated from the 28-row HMD `xpath` alignment. The semantic columns and fact model are unchanged, so the prior semantic validation is reused and is not described as regeneration evidence.
- Canonical publication metadata, README files, manifests, and the XBRL taxonomy LF policy were updated in WORK only. Formal GIT copy, stage, commit, push, and GitHub publication were not performed. Evidence: `docs/ChatGPT/2026/202609/20260911/20260911_0850/taxonomy-publication-layout-canonical-resolution/outputs/`.

## 2026-09-11 Formal GIT publication baseline

- UADC-PoC accepted base `b071f6fcc76f240a90665c2f380a1d4ce1ca2d27` was fast-forwarded to `f6427e34f3931acabc34aa63891f9c7dec262bf3` on `origin/main`.
- The published change has 4 ADD and 17 UPDATE paths; the other 17 accepted UADC paths remain byte-identical KEEP resources. No deletion was published.
- Fresh sibling worktrees resolved all 12 monthly metadata references to `XBRL_GL_Next/taxonomy/accounting-entries`; MODEL/PUBLIC manifests passed 37/37 and Arelle 2.37.77 passed 14/14 with error 0 and warning 0.
- Existing synthetic outputs were not regenerated after the V14 HMD xpath-only revision. Non-empty counterparty preservation remains unverified because the accepted inputs contain zero non-empty counterparty occurrences.
- Evidence: `docs/Codex/2026/202609/20260911/20260911_0932/formal-git-publication/outputs/`.

## 2026-09-13 PCA 81列順変換のWORK追加登録

- 16列PCA Binding用汎用`csv2tidy.py`を`models/xbrl-gl-next/accounting-entries/scripts/`へ追加。既存13列版、`flat_csv.py`及びその利用先は置換していない。
- 匿名評価profile、mapping、ZIP版taxonomy閉包、入力、独立テストは`data/private/anonymized/pca-csv2tidy-review-r1/`に内部限定で配置。HMDは同一SHAのWORK model unit正本を参照する。ZIP版taxonomyとmodel unit既存taxonomyは同一SHAではなく、混在させない。
- 5,148入力行、2,847伝票、9,043借貸明細、借貸各4,348,168,879円を独立照合。構造ツリー44,391出現のうちfact無しルート1件を除く正式xBRL-CSVは44,390データ行・26列。Arelle 2.37.77は登録先生成JSONを終了コード0、エラー0、警告0で検証した。
- DatePostedの日付→午前0時の意味確認、専用取引先列と補助由来の取引先・銀行参照、逆変換、他profileは未受入。公開・Official GIT反映・commit・pushは未実施。証跡は`docs/Codex/2026/202609/20260913/20260913_1330/pca-csv2tidy-revision-validation/outputs/`。

## 2026-09-15 ns20 Canonical WORK baseline

- `20260915_0849/ns20-extracted/candidate`のmanifest payload 95件中、package `README.md`を除く94件をCanonical WORKへ配置した。ADD 70、UPDATE 13、KEEP 11で、配置後SHAは94/94一致する。
- 入力PCA、生成EPSON、roundtripは`instances/original`、`instances/derived`、`instances/roundtrip`のprofile別subdirectoryに分離した。科目名と銀行補助名の分離、独立枝番だけで異科目を対応させない制約を候補バイトのまま維持した。
- Arelle 2.37.77既存PASSはPCA 130,807、EPSON 134,281 fact rows、error 0、warning 0。正規配置後静的確認はSHA 94/94、JSON参照4/4、XML closure 22件、修正namespace 6/6でPASS。
- 税額fact未保存141,601,937円・3,490明細、`TAX_POLICY_AMBIGUOUS`、EPSON科目登録・実アプリ取込未確認は未解決。開始残高と別EPSON実原本は範囲外。
- 上流生成器は旧namespaceを生成するため再発防止未完了。公開はnamespace承認文書及びD-052 split taxonomyとの`AUTHORITY_CONFLICT / HOLD`。Official GIT、stage、commit、pushは未実施。
- 証跡: `docs/Codex/2026/202609/20260915/20260915_0913/ns20-canonical-promotion/outputs/`。

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
