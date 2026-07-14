# UADC セットアップ、定義、テスト環境

## コンテンツの表

1. [目的](#1-purpose)
2. [リポジトリレイアウト](#2-repository-layout)
3. [クローンとPythonのセットアップ](#3-clone-and-python-setup)
4. [ディフェンステーブル](#4-definition-tables)
5. [証拠例と生成](#5-samples-and-generated-evidence)
6. [環境検証](#6-environment-verification)
7. [回帰テスト](#7-regression-tests)
8. [内部試験](#8-test-internals)
9. [GitHub ワークフロー](#9-github-workflow)
10. [文書 PDFワークフロー](#10-documentation-pdf-workflow)
11. [トラブルシューティング](#11-troubleshooting)
12. [開発環境・メンテナンス](#12-development-environment-and-maintenance)
13. [機械読みやすい仕様ファイル](#13-machine-readable-specification-files)
14. [リポジトリファイルと証拠](#14-repository-files-and-evidence)
15. [完全テストとラウンドトリップ手順](#15-complete-test-and-round-trip-procedure)

## 1. 目的

このドキュメントでは、 UADC PoC で使用される GitHub のワークスペースを準備して検証する方法について説明します。 編集可能で生成されたEN 16931、UBL、ADS、およびISO 21378 ADC定義テーブル、必要なPython環境、テストプログラム、およびコミットされた出力証拠を識別します。

処理ガイドは別です:

- **TUTORIAL.md**ショートエンドツーエンドのウォークスルーを提供します。
- **SYNTAX_BINDING.md**Phase 1 を指定します。
- **SEMANTIC_BINDING.md**Phase 2 を指定します。
- **DATA_MODEL.md**一般的なモデル、タクソノミ、およびサポートツールを指定します。

## 2. リポジトリレイアウト

|ディレクトリ | 役割 |
|---|---|
| **ログイン**| 運用 Phase 1 および Phase 2 コンバーター |
| **src/tutorial/**| 業務用コンバーターを呼び出す初心者用ラッパー |
| **ツール/**| 定義メンテナンス、タクソノミ生成、アーティファクト生成、検査工具 お問い合わせ
| **tools/tutorial/**| 学習と実験のための簡易コンバーターの実装 |
| **テスト/テスト**| 直接実行可能な回帰スクリプトとヘルパー。 |
| **スペック/**|LHM、バインディング、通貨、XBRL GLの定義表 |
| **サンプル/**| 入力XMLと予想サンプルデータを同梱 |
| **アウト/**| 生成されたタクソノミ、Phase 1、Phase 2、逆、チュートリアル、およびGitが追跡したQA証拠。 |
| **ドキュメント/**| 5つの観音ガイドと決定記録 |

各スクリプトディレクトリには短いものが含まれています**README.md**GitHubで閲覧できます。 5つの書類**ドキュメント/**権威ある操作と実装ガイドです。

## 3. クローンとPythonのセットアップ

### 3.1 WindowsのPowerShell

```
git clone https://github.com/pontsoleil/UADC-PoC.git
cd .\UADC-PoC
$python = 'python'
& $python --version
```

Pythonがない場合**パス**は、インストールされた実行可能なパスを使用します。

```
$python = 'C:\Users\<user>\AppData\Local\Programs\Python\Python310\python.exe'
& $python --version
```

### 3.2 macOSまたはLinux

```
git clone https://github.com/pontsoleil/UADC-PoC.git
cd ./UADC-PoC
PYTHON=python3
$PYTHON --version
```

### 3.3 コアコンパイルチェック

```
& $python -m py_compile `
  .\src\syntax_binding.py `
  .\src\semantic_binding.py `
  .\src\syntax_binding_ads_xbrl_gl.py
```

すべてのPythonプログラム**ツール/**で点検することができます:

```
Get-ChildItem .\tools -Recurse -Filter *.py | ForEach-Object {
  & $python -m py_compile $_.FullName
}
```

## 4. 定義テーブル

### 4.1 EN 16931 LHM

|ファイル | 目的 |
|---|---|
| **specs/lhm/source/EN16931_CIUS_Invoice_LHM_Source.csv**| 業務条件・上書きコラムを含む編集可能情報 |
| **specs/lhm/EN16931_CIUS_Invoice_LHM.csv**| コンバーターとタクソノミ生成で消費される操作LHMを生成。 |
| **specs/lhm/EN16931_CIUS_Invoice.xlsx**| ローカルレビュアーブック、ランタイムの権限ではありません。 |

LHM は、セマンティック階層、クラス、属性タイプ、multiplicity を記録し、有効**lhm  レベル**, 意味パス, 要素名, データ型, UBL XPath.

### 4.2 Phase 1 UBL 構文バインディング

操作UBL Invoiceの結合はあります:

```
specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv
```

クラス行と実際の行の両方が含まれています。 XMLの位置、selector、Structured CSV列、および繰り返し 行スコープ のランタイム権限です。

### 4.3 Phase 2 ADS XBRL GL ビンディング

6つの構文結合CSV**specs/bindings/syntax/**定義:

- インボイスs 受信;
- インボイス 生成される;
- インボイス 受信行;
- インボイス 生成されたライン;
- サプライヤーリスト;
- 顧客マスター。

レビューワークブックは:

```
specs/bindings/ADS_XBRL_GL_Bindings.xlsx
```

### 4.4 Phase 2 ADS PSV ビンディング

CSVの6つのセマンティック結合**specs/bindings/semantic/**同じヘッダー、ライン、サプライヤー、および顧客ターゲットファミリーを delimiter-separated ファイルとして定義します。

### 4.5 ISO 21378 ADC ビンディング

ISO 21378:2019年4月 インボイス 閲覧数:

```
ISO21378_SAL_Invoice_Generated_CSV_Binding.csv
ISO21378_SAL_Invoice_Generated_Details_CSV_Binding.csv
ISO21378_PUR_Invoice_Received_CSV_Binding.csv
ISO21378_PUR_Invoice_Received_Details_CSV_Binding.csv
```

表38、39、53、54を表しています。 マッピング状態とノートは、直接値、近似、変換、およびERPの情報はEN 16931から利用できません。 インボイス

### 4.6 参照テーブル

- **specs/Currency.csv**ISO 4217の通貨コードをマイナー単位にマップします。
- **specs/CountryCurrency.csv**country/currency のデータを提供します。
- **specs/XBRL-GL/**結合に使用する XBRL GL 定義参照を含んでいます。

## 5. サンプルおよび生成された証拠

### 5.1 Phase 1 入力

```
samples/input/openpeppol_ubl_invoice_minimal.xml
samples/input/bis-billing3-examples/*.xml
```

現在の回帰セットには、最小限のインボイスと9つのBIS Billing 3の例が含まれています。

### 5.2 出力レイアウト

```
out/taxonomy/
out/phase1/
out/phase2/ADS_XBRL_GL/
out/phase2/ADS_PSV/
out/phase2/ISO21378_ADC/
out/reverse/
out/tutorial/
```

生成された証拠はレビューのために託されます。 手動で編集するのではなく、定義とスクリプトから再生します。

## 6. 環境の検証

チュートリアル前提条件チェックを実行します。

```
& $python .\src\tutorial\00_check_environment.py
```

3つの操作スクリプト、 タクソノミ ジェネレータ、 LHM、 UBL および ADS 結合、および最小限のサンプルを検証します。 未生成の タクソノミ は、不足しているソース定義ではなく、次のアクションとして報告されます。

必要に応じてローカル タクソノミ を生成し、検証します。

```
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tests\validate_taxonomy.py
```

オプションの依存関係:

|依存症 | 目的 |
|---|---|
| **Arelle**|xBRL-CSVメタデータとXBRLタクソノミまたはインスタンス検証 |
| **xmlschemaさん**| UBL 2.1 往復スキーマ検証 |
| **サイトマップ**| EN 16931PDF対応のカバレッジ監査 |
| **pdfplumberの特長**| 更新 LHM の定義から EN 16931 表2. |

## 7. 回帰テスト

Tests は Python スクリプトをプレーンし、直接実行できます。

### 7.1 Phase 1

```
& $python .\tests\test_lhm_semantic_paths.py
& $python .\tests\test_lhm_hierarchical_csv_layout.py
& $python .\tests\test_syntax_binding.py
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_bis_billing3_examples_conversion.py
& $python .\tests\test_roundtrip_artifacts.py
& $python .\tests\test_roundtrip_xml_ubl_schema.py
& $python .\tests\test_xbrl_csv_metadata_arelle.py
```

### 7.2 Phase 2 ADS XBRL GL

指定されたすべてのターゲット固有のスクリプトを実行します**test ads *_xbrl_gl.py の**続いて:

```
& $python .\tests\test_phase2_outputs_by_structured_csv_stem.py
```

### 7.3 Phase 2 セマンティック出力

```
& $python .\tests\test_ads_invoices_received_psv.py
& $python .\tests\test_ads_invoices_generated_psv.py
& $python .\tests\test_semantic_binding_csv_format.py
& $python .\tests\test_semantic_binding_indexed_paths.py
```

### 7.4 完全な直接操業

```
Get-ChildItem .\tests\test_*.py | Sort-Object Name | ForEach-Object {
  & $python $_.FullName
  if ($LASTEXITCODE -ne 0) { throw "Failed: $($_.Name)" }
}
```

最新の記録された実行は、失敗なしで22スクリプトを完了しました。

## 8. 内部をテストして下さい

Tests は、現在の Python 実行可能でサブプロセスコマンドを作成して、コンバータとテストは同じ環境を使用します。**phase1_helpers.py**Phase 1 結合パスと変換ヘルパーをターゲットテストで集中化します。

往復ビルダーは、ソースXML、Structured CSV、メタデータJSON、および再生UBLXMLの4つのアーティファクトフォルダを再作成します。 スキーマテストでは、バイト単位の ID ではなく、XML の妥当性を確認します。 Arelle はメタデータ JSON とその タクソノミ の参照をチェックします。

ターゲットテストは、セマンティックな事実、階層、 selectors、 行スコープs、 XBRL GL のタプル配置、月経小数、および出力命名を主張します。 これらは、煙テストだけでなく、回帰契約です。

## 9. GitHubワークフロー

仕事の前に:

```
git status --short
git pull --ff-only
```

変更後:

1. 関連する集中テストを実行します。
2. 共有モデルまたはコンバーターの変更のための完全な回帰セットを実行します。
3. コミットされた出力証拠を再生します。
4. 文書 PDF を変更しました。
5. レビュー**git 差分**そして、**git ステータス**.
6. 意図したブランチにコミットし、プッシュします。

結合 CSV とソース LHM の定義は、ソース ファイルのレビューです。 生成されたCSV、JSON、XML、XSD、リンクベース、およびPDFの証拠は、それらのファイルとコミットされたスクリプトから再現性を維持しなければなりません。

## 10. 文書 PDF ワークフロー

Markdownは編集可能なソースです。 PDF は、設定されたマージンを使用して、VSCode Markdown PDF 拡張機能で生成されます。

- 上および底:**20ミリメートル**;
- 左と右:**18ミリメートル**.

エクスポート後、最初のページと最後のページと大きなテーブルやコードブロックを含む任意のページを調べます。 マークダウンと対応するPDFを一緒にコミットします。

### 10.1 日本語の再生 文書

マークダウンが生成される**ログイン**ファーストパーティプロジェクト文書を含むすべてのディレクトリのサブディレクトリ。 英語のマークダウンは構造的なソースのままです。 プロジェクト用語と承認された日本語表現は、**docs/ja/TERMINOLOGY.csv**.

用語集 CSV は、これらの列を使用します。

|コラム | 目的 |
| --- | --- |
| **source term メソッド**| 源泉マークダウンの英語表記 |
| **ja termについて**| 生成された文書に挿した日本語表現 |
| **定義 ja**| 意図した意味を調べるために使用される日本の定義 |
| **マッチモード** | **リテラル**ケースに敏感な識別子または**フレーズ**自然言語のマッチングに。 |
| **パスワード**| 編集長・略歴・複数形ノート |

ExcelでCSVを編集し、そのまま保存**CSV UTF-8(カンマ区切り)**.保存したファイルがUTF-8 BOMを保持していることを確認します。 発電機はそれをと読みます**utf-8シグ**ですから、BOMは最初の列名から受け付け、除外されます。

リポジトリのルートから、すべての日本語のMarkdownを再生します。

```powershell
$python = 'C:\Users\nobuy\AppData\Local\Programs\Python\Python310\python.exe'
& $python .\tools\translate_markdown_ja.py
```

ローカルArgosはランタイムを翻訳し、日本語モデルには既に存在しなければなりません。**.translation runtime/ .translation runtime/**そして、**.translation data/ .translation data/ .translation data/**. これらの大きなローカル依存関係は、Git によって無視されます。 ジェネレータは、文書のテキストを外部の翻訳サービスに送信しません。

書き換えなしで生成されたセットを検証します。

```powershell
& $python .\tools\translate_markdown_ja.py --check
```

チェックは、サポートされているすべての英語のMarkdownファイルには日本語のカウンターパートがあり、コードフェンスのカウントマッチがあり、すべての出力には日本語のテキストが含まれています。 出版物の前に, また、用語の見直し, 相対リンク, テーブル, コマンド, パス, XPath, そして、不変の保護マーカーの欠如. 修正する**ja termについて**次のフルランで生成されたすべての日本語文書に適用されます。

## 11. トラブルシューティング

### 11.1 Pythonが見つかりません

セット**$パイソン**または**ピソン**絶対実行可能なパスへ。

### 11.2 PDFツールは、依存関係をインポートできません

選択したPython環境で必要なパッケージだけをインストールするか、オプションのPDF対応のメンテナンスアクションをスキップします。

### 11.3 Arelle または UBL スキーマの検証は利用できません。

残りのテストを実行し、省略された外部検証を明示的に報告します。

### 11.4 生成された出力は予想外に異なります

アクティブバインディングパス、入力ステム、エンコーディング、タクソノミバージョン、通貨テーブル、および出力が運用スクリプトで再生されたかどうかを確認します。**ログイン**単純化されたチュートリアルツールではなく。


## 12. 開発環境・整備

### 開発とツーリングガイド

このガイドでは、クローンタイムの設定、ローカル開発チェック、モデルメンテナンスツールについて説明します。

#### ディレクトリの役割

```
src/      operational conversion scripts
tools/    setup, model maintenance, taxonomy generation, and test artifact helpers
tests/    regression checks
specs/    committed LHM, binding, currency, and model definition CSVs
samples/  committed sample XML and expected outputs
out/      generated PoC evidence and target output tracked by Git
```

メイン インボイス 変換ランタイムは**ログイン**. 使用**ツール/**セットアップ、再生、テストアーティファクトビル、タクソノミの出力および指定の維持のため。

#### クローン後の初期設定

WindowsのPowerShell:

```
git clone https://github.com/pontsoleil/UADC-PoC.git
cd .\UADC-PoC
$python = 'python'
& $python --version
```

**$python = 'python' ディレクティブ**たとえば、PowerShell 変数代入です。 つまり、Python の実行可能を実行できます。**パス**. Python がない場合**パス**, フル実行可能なパスに設定します。

```
$python = 'C:\Users\<user>\AppData\Local\Programs\Python\Python310\python.exe'
& $python --version
```

macOS または Linux のシェル:

```
git clone https://github.com/pontsoleil/UADC-PoC.git
cd ./UADC-PoC
PYTHON=python3
$PYTHON --version
```

使用条件**$ピソン script.py**に macOS/Linux. 使用**と $python script.py**WindowsのPowerShellだけ。

#### コンパイルコアスクリプト

広いチェックを実行する前にコンパイル:

```
& $python -m py_compile `
  .\src\syntax_binding.py `
  .\src\syntax_binding_ads_xbrl_gl.py `
  .\src\semantic_binding.py `
  .\tools\build_roundtrip_test_artifacts.py `
  .\tools\taxonomy\xBRLGL_TaxonomyGenerator.py
```

macOS/Linux 等価:

```
$PYTHON -m py_compile \
  ./src/syntax_binding.py \
  ./src/syntax_binding_ads_xbrl_gl.py \
  ./src/semantic_binding.py \
  ./tools/build_roundtrip_test_artifacts.py \
  ./tools/taxonomy/xBRLGL_TaxonomyGenerator.py
```

#### ツールの分類

GitHubと開発環境のサポート:

```
build_roundtrip_test_artifacts.py
psv_viewer.html
```

転換ターゲット モデル環境サポート:

```
taxonomy/xBRLGL_TaxonomyGenerator.py
build_lhm_from_source.py
build_syntax_binding.py
normalize_lhm_semantic_paths.py
normalize_lhm_class_element.py
check_lhm_class_element.py
audit_en16931_coverage.py
extend_en16931_lhm_coverage.py
order_lhm_by_en16931_table2.py
update_lhm_definitions_from_pdf.py
update_lhm_syntax_sequence_from_ubl_xsd.py
```

チュートリアルとサンプルコンバータ:

```
tools/tutorial/syntax_binding_sample.py
tools/tutorial/semantic_binding_sample.py
```

操作ランタイムコンバーターは**ログイン**, ない**ツール/**.

#### モデル 入力および生成された出力

コミットされたソース定義:

```
specs/lhm/EN16931_CIUS_Invoice_LHM.csv
specs/bindings/syntax/
specs/bindings/semantic/
specs/Currency.csv
```

ローカル出力を生成する:

```
out/taxonomy/
out/phase1/
out/phase2/
tests/roundtrip/
```

**アウト/**生成された証拠とターゲット出力を含みます。 現在のPoCのGitにPhase 1とPhase 2結果がGitHubで確認できる状態に含まれています。 手動で編集するのではなく、ソースの定義とスクリプトからコミットされた出力を再生します。

詳細 目的, input/output, コマンドライン, 処理, 関数, 検証, 依存性, 全15プログラムの副作用仕様**ツール/**ドキュメント**DATA_MODEL.md**.

#### タクソノミ 生成

プライマリスクリプト:

```
tools/taxonomy/xBRLGL_TaxonomyGenerator.py
```

ロール:

```
LHM CSV -> local xBRL-CSV taxonomy for Structured CSV metadata
```

回帰チェックで生成および検証:

```
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tests\validate_taxonomy.py
```

期待されるローカル出力は下記のものを含んでいます:

```
out/taxonomy/en16931/en16931-2026-07-05.xsd
out/taxonomy/gen/gl-gen-2026-07-05.xsd
out/taxonomy/plt/en16931-oim-2026-07-05.xsd
out/taxonomy/plt/en16931-def-2026-07-05.xml
```

**src/syntax_binding.py**タクソノミ ファイルを生成しません。 それらを参照する**--taxonomy-base**xBRL-CSV メタデータ JSON を書くとき。

#### LHM メンテナンス

スクリプト:

```
build_lhm_from_source.py
normalize_lhm_semantic_paths.py
normalize_lhm_class_element.py
check_lhm_class_element.py
audit_en16931_coverage.py
extend_en16931_lhm_coverage.py
order_lhm_by_en16931_table2.py
update_lhm_definitions_from_pdf.py
update_lhm_syntax_sequence_from_ubl_xsd.py
```

LHM 編集後の典型的なチェック:

```
& $python .\tests\test_lhm_semantic_paths.py
& $python .\tests\test_lhm_hierarchical_csv_layout.py
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tests\validate_taxonomy.py
```

#### ビンディングメンテナンス

構文バインディング CSV は以下で動作します。

```
specs/bindings/syntax/
```

操作スクリプト:

```
src/syntax_binding.py
src/syntax_binding_ads_xbrl_gl.py
```

構文バインディング 変更後:

```
& $python .\tests\test_syntax_binding.py
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_ads_supplier_listing_xbrl_gl.py
& $python .\tests\test_phase2_outputs_by_structured_csv_stem.py
```

ADS XBRL GL のバインディング変更時に、対象固有のテストを実行し、 Arelle で生成された代表インスタンスを検証します。 サプライヤーリストの変更は、その旨を検証しなければなりません**識別子Type=V**selector とその**識別子 郵便番号**同じベンダーの識別子参照に子供が残っています。

意味バインディング CSV は以下で動作します。

```
specs/bindings/semantic/
```

操作スクリプト:

```
src/semantic_binding.py
```

意味バインディングテーブルはターゲットテーブルの定義から始まり、**semantic_path**, **タイプ:**と**multiplicity**. コンバーターはからの源のコラムを導きます**semantic_path**と 行スコープ から**タイプ=C**バインディング表 の行。

意味バインディング 変更後:

```
& $python .\tests\test_ads_invoices_received_psv.py
& $python .\tests\test_ads_invoices_generated_psv.py
& $python .\tests\test_semantic_binding_csv_format.py
& $python .\tests\test_phase2_outputs_by_structured_csv_stem.py
```

#### ラウンドトリップアーティファクト再生

LHM、構文バインディング、またはタクソノミのメタデータ動作が変更されるとき:

```
& $python .\tools\build_roundtrip_test_artifacts.py
& $python .\tests\test_roundtrip_artifacts.py
```

アーティファクトショー:

```
source XML
Structured CSV
xBRL-CSV metadata JSON
regenerated UBL XML
```

#### 継続的な開発ワークフロー

編集の前に:

```
git status --short
```

runtime スクリプトの編集後:

```
& $python -m py_compile .\src\syntax_binding.py
& $python .\tests\test_syntax_binding.py
& $python .\tests\test_syntax_binding_reverse.py
```

LHM を編集するか、CSV ファイルを結合した後:

```
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tools\build_roundtrip_test_artifacts.py
& $python .\tests\test_roundtrip_artifacts.py
```

変更を共有する前に、 Arelle または UBL スキーマキャッシュが利用できない場合は、広いローカルチェックを実行し、明確に報告します。

#### psv_viewer.html

**tools/psv_viewer.html**生成された ADS PSV ファイルをブラウザテーブルとして表示します。 ブラウザで完全に実行され、ローカルWebサーバーを必要としません。 パイプ、コンマ、タブの区切り文字、行のフィルタリング、スティールヘッダ、水平スクロール、各データ行に空の列の自動非表示をサポートしています。



## 13. 機械読みやすい仕様ファイル

### 仕様ファイルガイド

このガイドでは、仕様ファイルについて説明しています。**スペック/**これらのファイルが定義され、維持される方法。

ふりがな**スペック/**ディレクトリには、UADCのPoC変換パイプラインで使用される機械で読みやすいCSV仕様が含まれています。 これらのファイルは、下にスクリプトに入力されます**ログイン**そして、**ツール/**. それらは小さい、見直し可能および決定的ままであるべきです。

#### ディレクトリマップ

```
specs/
  Currency.csv
  CountryCurrency.csv
  lhm/
  bindings/
  XBRL-GL/
```

#### 通貨テーブル

**Currency.csv**ISO 4217の通貨コードをマイナー単位にマップします。 XBRL GL 月 日 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 分 時 時 時 時 時 時 時 分 時 時 時 時 時 分 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時 時**デシマル**値。

典型的なコラム:

```
currency_code,minor_unit,currency_name
```

例:

```
JPY,0,Japanese Yen
EUR,2,Euro
```

**CountryCurrency.csv**通貨コードに国の例をマップします。 フィンランドやエストニアなどの国志向事例の参考データとして使われています。

例:

```
FI,Finland,EUR,2,Euro
EE,Estonia,EUR,2,Euro
```

Runtime XBRL ユニットは、ISO 4217 の通貨コードを使用します。**Currency.csv**.

#### LHM 仕様ファイル

LHM ファイルが下にある:

```
specs/lhm/
```

重要なファイル:

- **EN16931_CIUS_Invoice_LHM.csv**: 生成された EN 16931 インボイス LHM Structured CSV 変換と タクソノミ 生成によって消費されます。
- **source/EN16931_CIUS_Invoice_LHM_Source.csv**: 生成されたLHMを再生または調整するために使用される編集可能なソースCSV。
- **EN16931_CIUS_Invoice.xlsx**: ローカル査読者ワークブック Git では無視され、自動化によって更新されるべきではありません。

LHM は定義します。

- 意味パスs;
- クラスと要素名。
- multiplicity;
- 有効期間**lhm  レベル**;
- UBL XPath の結合の参照;
- Structured CSVとxBRL-CSVタクソノミ生成に必要なフィールド。

##### LHM ソース CSV

使用条件**specs/lhm/source/EN16931_CIUS_Invoice_LHM_Source.csv**PDF-derived EN 16931-1テーブル2項目への個々の調整のため。

生成の流れ:

```
python UADC_PoC/tools/build_lhm_from_source.py build `
  UADC_PoC/specs/lhm/source/EN16931_CIUS_Invoice_LHM_Source.csv `
  UADC_PoC/specs/lhm/EN16931_CIUS_Invoice_LHM.csv
```

オプションのオーバーライドカラム:

- **semantic_path オーバーライド**;
- **class term override(クラス)**;
- **要素 override**.

いつか**要素 override**ブランクで、ジェネレータは 意味パス からユニークな UpperCamelCase 要素名を作成します。 最後のパスセグメントが重複している場合は、最も短いユニークな意味パスサフィックスを使用します。

#### 仕様ファイルの結合

ファイルの結合は下にあります:

```
specs/bindings/
```

作者とコンバージョンルールの結合は、次のように記述します。

- **SYNTAX_BINDING.md**構文バインディング の場合;
- **SEMANTIC_BINDING.md**意味バインディング の場合;
- **DATA_MODEL.md**共有行適用範囲と関数レベルの処理モデルの場合。

結合ファイルは接続します:

- 入力構文 に UADC 皮膜モデル;
- UADC Structured CSV を下流対象の構文へ。
- UADC Structured CSV をフラットなセマンティックターゲットテーブルに。

#### XBRL GL 仕様ファイル

XBRL GL 定義テーブルの下にある:

```
specs/XBRL-GL/
```

重要なファイル:

- **xbrl-gl.csv**: XBRL GL 整列された定義テーブル**XBRL-GL-PWD-2016-12-01/gl/plt/case-c-b-m-u-e-t-s/gl-plt-all-2016-12-01.xsd**そして輸入されて**グルコア**, **グランバス**, **グラッシュ**, **グリーム**, **グルタフ**, **グラッシュ**と**グルースク**モジュール。

表は、利用可能な既存の英語と日本語のラベルを保持します。 選択されたXBRL GLタクソノミプロファイルから、シーケンス、モジュール名、カード名、タイプ名、および親子の注文が正規化されます。

ふりがな**XPath**列は、絶対的なタプルまたは実際のパスを記録します**xbrli:xbrl**。 タクソノミ 親子ツリーから生成されるので、バインディング表 は、内部行 ID を運ぶことなく、ターゲット XBRL GL の場所に直接ポイントすることができます。

#### メンテナンスルール

- スプレッドシートの編集が必要なCSVファイルUTF-8またはUTF-8 BOMを保持します。
- 記述はコンマを含むことができるので引用された分野を、保存する構造化されたCSVの作家かスプレッドシート用具を使用して下さい。
- ワークブックが明示的にレビューの成果物の一部である場合を除き、ローカルの査読者のワークブックの変更をコミットしないでください。
- 生成された CSV ファイルをソース CSV やスクリプトから生成し、生成されたファイルを手動で編集するのではなく、ジェネレータが存在するとき。
- 拘束力のあるデータを バインディング表 から保持します。 拘束力のある契約の一部を意図しないと。



## 14. リポジトリファイルと証拠

### リポジトリファイルガイド

このガイドでは、レポジトリサンプルファイル、予想ファイル、リファレンス、図アセットについて説明します。

#### サンプル

同封されたサンプルファイルは以下です。

```
samples/
```

サブディレクトリ:

- **入力/**: 変換テストで用いられるソースコードXMLサンプル。
- **予想/**: 集中された回帰点検によって使用される安定した予想される出力。

重要な入力ファイル:

- **samples/input/openpeppol_ubl_invoice_minimal.xml**: ベースライン OpenPeppol と EN 16931 変換チェックに用いられる最小 UBL Invoice のサンプル。
- **samples/input/bis-billing3-examples/**: より広い構文バインディングカバレッジをテストするために使用されるBIS Billing 3 インボイス例を選択します。

BISビルイング3例演習手当、VATカテゴリ、ネガティブ補正インボイス、販売注文基準、税務会計通貨処理。

生成されたStructured CSV、メタデータJSON、および再生されたXMLは保持されます**tests/roundtrip/**または**アウト/**, ない**サンプル/**.

#### 参考文献

軽量の参照材料は下にあります:

```
references/
```

ファイルとサブディレクトリ:

- **peppol_sources.md**: OpenPeppol と BIS Billing のソース素材のメモとリンク
- **数字/**: マークダウン文書の提案資料から抽出または準備された画像。

チェックされたソースページ:

- Peppol BIS Billing 3.0 リリース: https://docs.peppol.eu/poacc/billing/3.0/upcoming/
- UBL Invoice 構文ツリー: https://docs.peppol.eu/poacc/billing/3.0/upcoming/syntax/ubl-invoice/tree/
- EN 16931 UBL規則に拘束されたモデル: https://docs.peppol.eu/poacc/billing/3.0/upcoming/rules/ubl-tc434/

次のページでは、 EN 16931 のルールから UBL Invoice の構文 文書 を UBL に分割する 5 月 2026 リリースを識別します。

ローカル EN 16931 ベースセマンティックモデルに使用される参照**NEN-EN 16931-1 2017+A1_2019_en.pdf - 営業終了**. Clause 6.2 は、各情報要素とグループがどのように記述されているかを定義します。 条項6.3表2は、電子のコア要素の皮下データモデルインボイスです。

現在のLHM拡張子には、ドキュメントレベルの手当、文書レベルの料金、文書の合計、VATの故障、インボイス行、インボイス行の期間、インボイス行の手当、およびインボイス行の料金が含まれます。

OpenPeppol BIS Billing は EN 16931 のサブソースとしてではなく LHM の上にレイヤーされた CIUS と構文結合ソースとして扱われます。

#### プロフィール

図資産は以下のとおりです。

```
references/figures/
```

重要なファイル:

- **uadc poc processing flow figure1.png の処理**: 図1はPoCの提案から、OpenPeppol インボイスXMLから階層型Tidy Dataおよび下流の監査ビューまでの2段のUADC処理フローを表示します。

図を追加する場合は、記述名で安定したPNGファイルを好む。 トレーサビリティに有用である場合にのみ、中間レンダリングファイルを保持します。



## 15. 完全なテストおよび円形のトリップのプロシージャ

### 試験とラウンドトリップアーティファクトガイド

このガイドでは、テストの実行と往復レビューアーティファクトについて説明します。

コマンドを実行する**UADC ポック**ディレクトリ。 テストスクリプトは、Pythonスクリプトをプレーンし、直接実行できます。**$パイソン**。 いくつかは、また実行することができます**ピテスト**pytest がインストールされているとき。

#### 支持ファイル

- **tests/roundtrip/**:見直し可能な往復アーティファクト。 各ケースは、ソースXML、Structured CSV、xBRL-CSVメタデータJSON、およびXMLを一緒に再生します。
- **tools/build_roundtrip_test_artifacts.py**: サンプルXML入力から往復アーティファクトセットを再構築します。

#### Phase 1 構文バインディング テスト

これらのテストでは、XML から Structured CSV、 xBRL-CSV メタデータ、および UBL 往復動作を確認します。

```
& $python .\tests\test_openpeppol_invoice_conversion.py
& $python .\tests\test_lhm_hierarchical_csv_layout.py
& $python .\tests\test_syntax_binding.py
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_ubl_schema_child_order.py
& $python .\tests\test_bis_billing3_examples_conversion.py
& $python .\tests\test_roundtrip_artifacts.py
```

転送 Phase 1 変換は、XML の親コンテキスト再帰を使用しており、 反復クラス は親 ディメンション などの値を保持します。**dInvoiceLine**お子様と一緒に ディメンション など**dItemAttributes**.

逆変換は、XSDファイルからXSDファイルからUBLの子要素オーダーを導き出すことができます。**--ubl-schema-root**または**--ubl-schema-url**. **test_ubl_schema_child_order.py**完全なUBLパッケージをダウンロードすることなく、このXSD由来のオーダーロジックを確認してください。

**test_syntax_binding_reverse.py**また、cross-適用範囲 絶対XPath 処理: BT-90 は root 以下に記述する必要があります。**アカウンティングサプライヤーパーティー**と**PaymentMeans/Invoice**存在しない。**test_bis_billing3_examples_conversion.py**通貨フィルタの合計をチェックイン**Allowance-example.xml**: BT-110 は**1225.00**と BT-111 は**9324.00**.

#### Phase 2 ADS XBRL GL テスト

これらのテストは Phase 1 Structured CSV を最初に再生し、ADS XBRL GL 構文バインディング CSV ファイルを下で使用します**specs/bindings/syntax/**.

```
& $python .\tests\test_ads_invoices_received_xbrl_gl.py
& $python .\tests\test_ads_invoices_generated_xbrl_gl.py
& $python .\tests\test_ads_invoices_received_lines_xbrl_gl.py
& $python .\tests\test_ads_invoices_generated_lines_xbrl_gl.py
& $python .\tests\test_ads_supplier_listing_xbrl_gl.py
& $python .\tests\test_ads_customer_master_xbrl_gl.py
```

期待される出力:

```
out/phase2/ADS_XBRL_GL/<structured-csv-stem>/<target-view>.xbrl
```

対象ビュー ファイル:

```
Invoices_Received.xbrl
Invoices_Generated.xbrl
Invoices_Received_Lines.xbrl
Invoices_Generated_Lines.xbrl
Supplier_Listing.xbrl
Customer_Master.xbrl
```

**test_ads_supplier_listing_xbrl_gl.py**売り手 の名前と ID が書かれていることを確認します。**識別子Type=V**識別子参照とその 売り手 通り、市街地、国、郵便番号は下記の通りです。**gl-bus:identifierアドレス**タプル。

#### Phase 2 ADS PSV CSVテスト

これらのテストでは、 意味バインディング のファイルを使用します。**specs/bindings/semantic/**.

```
& $python .\tests\test_ads_invoices_received_psv.py
& $python .\tests\test_ads_invoices_generated_psv.py
& $python .\tests\test_semantic_binding_indexed_paths.py
& $python .\tests\test_semantic_binding_csv_format.py
& $python .\tests\test_phase2_outputs_by_structured_csv_stem.py
```

期待される出力:

```
out/phase2/ADS_PSV/<structured-csv-stem>/<target-view>.psv
```

#### タクソノミ および LHM チェックイン

```
& $python .\tests\test_lhm_semantic_paths.py
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tests\validate_taxonomy.py
```

#### ラウンドトリップアーティファクト

往復の流れ:

```
source XML -> Structured CSV -> regenerated XML
```

アーティファクトは以下です。

```
tests/roundtrip/<dataset>/
  source_xml/
  structured_csv/
  metadata_json/
  roundtrip_xml/
```

現在のデータセット:

```
tests/roundtrip/openpeppol-minimal/
tests/roundtrip/bis-billing3-examples/
```

再構築:

```
$python = 'python'
& $python .\tools\build_roundtrip_test_artifacts.py
```

確認:

```
& $python .\tests\test_roundtrip_artifacts.py
```

ソースXML、Structured CSV、メタデータJSON、および往復XML対応をチェックします。 などの代表値もチェックします。**インボイス番号**, **ドキュメント通貨コード**, **インボイスライン識別子**, 量**通貨ID**, タクソノミ エントリ ポイント, xBRL-CSV 列の概念マッピング.

#### オプションの検証

Arelleメタデータ検証:

```
& $python .\tests\test_xbrl_csv_metadata_arelle.py
```

UBL 2.1 スキーマ検証:

```
& $python .\tests\test_roundtrip_xml_ubl_schema.py
```

再生成されたXMLは、XMLと同じバイトバイト単位であることは期待できません。 境界CSV値から再構築され、XML宣言書式、名前空間配置、インデント、およびアンバウンドXMLコンテンツと異なる場合があります。

#### 現在のテスト実行レポート

過去の記録されたレポートの日付:

```
2026-07-14
```

記録された結果:

```
PASS
```

全22セット**tests/test_*.py**回帰スクリプトは、2026-07-14 に 2 つの単純化したコンバーターの実装を移動した後に実行されました。**tools/tutorial/**. 全22は失敗なしで首尾よく完了しました。 全14のPythonプログラム**ツール/**渡される**パイ コンパイル**.

適用範囲 EN 16931 LHM 駆動 構文バインディング 変換, Structured CSV 生成, xBRL-CSV メタデータ生成, Arelle 検証, UBL 逆変換, BIS 請求 3 変換, LHM チェック, ローカル タクソノミ 生成チェック.

taxonomy/LHM チェック、OpenPeppol 変換、BIS Billing 3 変換、Structured CSV メタデータ、10 往復アーティファクト ケース、および Arelle のすべての 10 xBRL-CSV メタデータ ファイルが渡された検証。 絶対通貨フィルタ XPath の評価が修正されたので**Allowance-example.xml**BT-110 を書こう**1225.00**と BT-111 として**9324.00**. すべての Phase 2 ADS XBRL GL および ADS PSV/CSV の出力が再生され、テストが渡されました。

製造者リスト XBRL GL の結合は 売り手 の郵便住所の事実とそれから完了しました**識別子Type=V**識別子の参照。 サプライヤーリストは、全ての10個のPhase 1入力から再生成され、10個の結果が**Supplier_Listing.xbrl**Arelle バリデーションを渡したインスタンス。 4つのISO 21378 ADC インボイスバインディングは、すべての10 Phase 1入力に適用され、40 CSVターゲットファイルを生成しました。 詳細なISOフィールドのカバレッジと既知のソースデータギャップが記録されます**SEMANTIC_BINDING.md**, 第19章.

これらの結果は計画されたPhase 1およびPhase 2PoCのベースラインを完了しました。 ISO 21378の完了は、4つの計画されたインボイスビュー、それらのマッピング、出力、およびギャップの分類が完了していることを意味しています。 EN 16931はISO 21378によって定義されているすべての監査システムフィールドが含まれているという意味ではありません。

リバースコンバーターは、セマンティック子が繰り返された構文のコンテキスト外に保存されるときに、UBL文書でルーティングされた絶対結合XPathを保持します。 ネストされたものからBT-90を防ぐ**インボイス**お問い合わせ**支払方法**。テストが含まれている環境と動くときすべての10の再生された往復XMLファイルはUBL 2.1 インボイススキーマの検証を渡します**xmlschemaさん**.
