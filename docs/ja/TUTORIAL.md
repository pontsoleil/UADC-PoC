# UADC エンドツーエンドチュートリアル

## コンテンツの表

1. [目的](#1-purpose)
2. [チュートリアルフロー](#2-tutorial-flow)
3. [環境チェック](#3-check-the-environment)
4. Phase 1 Structured CSV(#4-generate-phase-1-structured-csv)
5. [ラウンドトリップからUBL XMLへ](#5-round-trip-to-ubl-xml)
6. Phase 2 ADS XBRL GL 閲覧](#6-generate-a-phase-2-ads-xbrl-gl-view)
7. 結果(#7-inspect-the-results)を調べる
8. [内部でHappensとは](#8-what-happens-internally)
9. [簡易チュートリアル実装](#9-simplified-tutorial-implementations)
10. [次工程](#10-next-steps)

## 1. 目的

このチュートリアルでは、長いコマンドをビルドするリーダーを必要としない一般的なUADCフローを示しています。**src/tutorial/**の下のスクリプトは、フル Phase 1 と Phase 2 のワークフローで使用される同じ操作コンバーターを呼び出します。

リポジトリのルートからすべてのコマンドを実行します。

## 2. チュートリアルフロー

```
UBL Invoice XML
  -> Phase 1 syntax binding
  -> Structured CSV and xBRL-CSV metadata
  -> reverse syntax binding
  -> regenerated UBL Invoice XML

Structured CSV
  -> Phase 2 ADS syntax binding
  -> ADS Invoices Received XBRL GL
```

チュートリアル出力は**out/tutorial/**.で書かれています。

## 3. 環境チェック

WindowsのPowerShell:

```
$python = 'python'
& $python .\src\tutorial\00_check_environment.py
```

スクリプトレポート:

- Pythonの実行可能;
- 検出されたリポジトリのルート;
- 運用スクリプトや定義の欠如;
- 生成された OIM タクソノミ エントリ ポイントが既に存在するかどうか。

内部的に、**REQUIRED PATHS**はLHM、UBLおよびADS結合、サンプルXML、ランタイムコンバータ、往復ビルダー、およびタクソノミジェネレータをリストします。 必要なソースファイルが見つからない場合、スクリプトはステータス**1**を返します。

## 4. 発生Phase 1 Structured CSV

```
& $python .\src\tutorial\01_convert_sample_to_structured_csv.py
```

入力:

```
samples/input/openpeppol_ubl_invoice_minimal.xml
```

出力:

```
out/tutorial/openpeppol_ubl_invoice_minimal.csv
out/tutorial/openpeppol_ubl_invoice_minimal.json
```

**ensure タクソノミ**を呼び出します。 ローカル タクソノミ が見つからない場合は、タクソノミ ジェネレータ回帰スクリプトを実行します。**src/syntax_binding.py**を EN 16931 UBL 結合、メタデータ出力パス、 タクソノミ ベースで呼び出します。

CSVを開き、観察します。

- **dInvoice**インボイス 行;
- 繰り返されたインボイスラインまたはVATの故障のための別の列;
- それらを所有するクラス外でセルをスパーズ;
- LHM 要素の定義から指定された事実の列。

JSON を開き、OIM ドキュメントタイプ、 タクソノミ エントリーポイント、テーブルテンプレート、 ディメンション、コンセプト、通貨単位を観察します。

## 5. UBL XMLへのラウンドトリップ

```
& $python .\src\tutorial\02_roundtrip_structured_csv_to_xml.py
```

出力:

```
out/tutorial/openpeppol_ubl_invoice_minimal.roundtrip.xml
```

**ensure structd csv**は、必要に応じて以前のチュートリアルステップを実行します。**--reverse**と**--reverse**と同じ UBL の結合。

再生されたXMLは、バイト単位のコピーではなく、セマンティック出力です。 名前空間配置、インデント、XML宣言、およびアンバウンドコンテンツは異なる場合があります。 重要なチェックは、バインド値、階層、UBLの子注文、およびスキーマの妥当性です。

## 6. Phase 2 ADS XBRL GL を生成する ニュース

```
& $python .\src\tutorial\03_generate_ads_xbrl_gl.py
```

出力ディレクトリ:

```
out/tutorial/xbrl-gl/
```

ラッパーの使用:

```
src/syntax_binding_ads_xbrl_gl.py
specs/bindings/syntax/ADS_Invoices_Received_XBRL_GL_Binding.csv
specs/lhm/EN16931_CIUS_Invoice_LHM.csv
specs/Currency.csv
```

生成されたインスタンスには、XBRL のコンテキストとユニットと XBRL GL で必要なタプル階層が 対象ビュー 含まれています。

## 7. 結果 の点検

### 7.1 Structured CSV

引用したCSVセルを保持するスプレッドシートエディタを使用します。 親 インボイス 行と繰り返された子行が関連のないクラスの事実を結合しないことを確認します。

### 7.2メタデータ JSON

タクソノミ エントリが タクソノミ であることを確認します。

```
out/taxonomy/plt/en16931-oim-2026-07-05.xsd
```

### 7.3 往復XML

実行:

```
& $python .\tests\test_syntax_binding_reverse.py
& $python .\tests\test_roundtrip_xml_ubl_schema.py
```

### 7.4 XBRL GL

Arelle で生成されたインスタンスをロードします。 タプル指向のレガシーサンプルと同じプレゼンテーションビューを期待するのではなく、タプル階層と事実を確認します。

### 7.5 PSVかCSV

delimiter-separated Phase 2 出力には、**tools/psv_viewer.html**を使用します。 ローカルでファイルを読み込み、パイプ、コンマ、タブ区切り文字、フィルター行をサポートし、ヘッダを目に見えるようにし、完全に空の列を非表示にします。

## 8. 内部でHappensが何であるか

チュートリアルラッパーは**subprocess.run**を**check=True**で使用します。 したがって、子コンバーターの故障はすぐにラッパーを停止します。

Phase 1 これらの内部の手順を実行します。

1. 負荷結合クラスおよび事実列;
2. derive ディメンション および直接クラス フィールド;
3. XML クラスのコンテキストを再帰的に歩きます。
4. 親行と子行を繰り返す。
5. 同じカラムとディメンションレイアウトでメタデータを書き込みます。

ディメンション による変換グループ行をリバースし、絶対結合 XPaths から XML ノードを再ビルドし、述語と属性を適用し、スキーマ由来の構文シーケンスから UBL の子を注文します。

ADS XBRL GL 生成は、実際の所有権を検証し、 対象ビュー のソース行を選択し、コンテキストと通貨単位を作成し、ターゲット XPaths に従い、 XBRL GL スキーマ順序で事実を記述します。

## 9. 簡易チュートリアルの実装

**tools/tutorial/**のプログラムは、上記のラッパーとは異なる。 学習および結合実験のためのより小さいコンバーターを実装します。

```
tools/tutorial/syntax_binding_sample.py
tools/tutorial/semantic_binding_sample.py
```

完全な階層列の所有権、繰り返し 適用範囲、メタデータ、リバース UBL、または Phase 2 動作を実行しません。 それらを使用して、PoC の成果物を生成しない小さなアルゴリズムを理解します。

## 10. 次のステップ

チュートリアルを完了した後:

1. LHM、 ディメンション、 Structured CSV ルールの**DATA_MODEL.md**をお読みください。
2. **SYNTAX_BINDING.md**をPhase 1バインディングを変更する前にお読みください。
3. ADS PSV、 ADS XBRL GL、または ADC を生成する前に**SEMANTIC_BINDING.md**をお読みください。
4. **SETUP.md**を使用して、関連する回帰と外部検証を実行します。
