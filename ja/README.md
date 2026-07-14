# UADC PoCコラボレーションワークスペース

このワークスペースは、xBRL-GL Next/UADCの概念の証明です。 「A 階層型Tidy Data 汎用監査データ変換器 for インボイス Reuse」 の 処理モデル を実行します。

UADC を 汎用監査データ変換器 と定義し、共通の意味で 階層型Tidy Data を使う。 ターゲットアーキテクチャは、ダウンストリームの監査ビュー生成から入力構文変換を分離します。

- 構文バインディング 地図ソース インボイス 共通 EN 16931 / XBRL GL 次の皮層;
- 一般的なセマンティック層は、文書レベルのインボイス情報、パーティー、税金のサブトタル、インボイスライン、識別子、日付、通貨、および金銭の量を保存します。
- 意味バインディング ISO 21378:2019 監査データ収集 Sales/Purchase インボイス ビューと AICPA ADS O2C/P2P インボイス ビューを含むダウンストリーム監査ビューに共通のデータセットをプロジェクトします。

このリポジトリは、その提案のための作業実装スペースです。 現在の実装は、計画されたPhase 1とPhase 2PoCベースラインを完了します。 Phase 1はEN 16931、Structured CSV、xBRL-CSV、タクソノミおよびメタデータ、検証、およびUBL ラウンドトリップを提供します。 Phase 2はADS XBRL GLおよびADS PSV 対象ビュープラス対象ビュー ADS XBRL GL ADS XBRL GLCSVビューを明示的なマッピングギャップ分類で提供します。

ADSとISO 21378 ADCは、ユーザーアクティビティの履歴をキャプチャし、詳細な経理記録が長期にわたる処理と年間レポートの準備に継続する、より広いERP環境を想定しています。 インボイス だけなので、すべての監査データフィールドを入力できません。 このPoCは、その境界の明示を行います: 監査ビューが インボイス のデータから派生することができることを示しています。フィールドは、変換や意味合いを要求し、どのフィールドが ERP レジャー、マスターデータ、ワークフローログ、またはその他の操作システムによって供給する必要があります。

ソースとターゲットインターフェイスファイルは、組織固有のままにすることができます。 これらのインターフェイスを共通のUADCに結合することによって、組織は保持されたデータの意味、階層、実証、検証ルールからアプリケーションフォーマットを変更することができます。 従ってPoCは従って監査で追跡可能そして使用可能な残っている安定した、長期データ保持のための実用的な基礎をERPプロダクトおよびインターフェイス フォーマットが時間とともに変えることを可能にする間示します。

最初のPoCチェックポイントはEN 16931-1 インボイスのセマンティックモデルでLHM/HMD-styleCSV、およびUBL InvoiceXMLから構造化されたCSV、xBRL-CSVJSONメタデータ、および往復UBL InvoiceXMLへの結合駆動変換。

OpenPeppol BIS Billing は、次のレイヤーとして扱われます。CIUS/profile は EN 16931-1 の上にオーバーレイされ、追加の制約、デフォルト、および構文固有のルールがあります。

## クローンとセットアップの概要

GitHubリポジトリをクローニングした後、このシーケンスを使用して、ローカルの実行と開発環境を準備します。

WindowsのPowerShell:

```
git clone https://github.com/pontsoleil/UADC-PoC.git
cd .\UADC-PoC
$python = 'python'
& $python --version
```

macOS / Linux シェル:

```
git clone https://github.com/pontsoleil/UADC-PoC.git
cd ./UADC-PoC
PYTHON=python3
$PYTHON --version
```

パワーシェルでは、**$python = 'python' ディレクティブ**変数代入であり、**と $python ...**PowerShell の呼び出し演算子を使用して、そのコマンドを実行します。 macOS/Linux シェルでは、**PYTHON=python3の特長**コマンドを実行する**$PYTHON ...**なし**&**. Python がない場合**パス**, 変数をフルローカルの Python 実行可能パスに設定します。

このリポジトリが大きいワークスペース内でチェックアウトされた場合、代わりにPoCディレクトリを入力してください。

```
cd <local-clone-directory>\UADC-PoC
```

次に生成されたローカルファイルとテストアーティファクトを用意します。

WindowsのPowerShell:

```
& $python -m py_compile .\src\syntax_binding.py .\tools\build_roundtrip_test_artifacts.py .\tools\taxonomy\xBRLGL_TaxonomyGenerator.py
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tools\build_roundtrip_test_artifacts.py
& $python .\tests\test_roundtrip_artifacts.py
```

macOS / Linux シェル:

```
$PYTHON -m py_compile ./src/syntax_binding.py ./tools/build_roundtrip_test_artifacts.py ./tools/taxonomy/xBRLGL_TaxonomyGenerator.py
$PYTHON ./tests/test_xbrlgl_generator_uadc_lhm.py
$PYTHON ./tools/build_roundtrip_test_artifacts.py
$PYTHON ./tests/test_roundtrip_artifacts.py
```

これは、下のローカルxBRL-CSV タクソノミを作成します**out/taxonomy/**見直し可能なラウンドトリップアーティファクトを下でリフレッシュ**tests/roundtrip/**.

環境設定とテストについては、**docs/SETUP.md**. エンドツーエンド学習フローについては、**docs/TUTORIAL.md**. 変換契約と実装の詳細は**docs/SYNTAX_BINDING.md**, **docs/SEMANTIC_BINDING.md**と**docs/DATA_MODEL.md**.

## 図1

![図1 - UADC PoC処理フロー](../references/figures/uadc_poc_processing_flow_figure1.png)

図1は、意図した UADC 処理フローを示しています。 Phase 1 は OpenPeppol/UBL インボイス XML から EN 16931 階層型Tidy Data、構造化された CSV、JSON メタデータ、 タクソノミ 検証、および往復 XML から Phase 2 のソースツー 意味パス をカバーしています。 Phase 2 は、ISO 21378 および AICPA ADS 対象ビュー に対して同じ皮膜層を 意味バインディング に拡張します。

## UADC 処理工程

下のフェーズでは、プロジェクト管理マイルストーンではなくUADC処理モデルを記述します。

|フェーズ | 処理工程 | 主な入出力 | 現在の状況 |
| --- | --- | --- | --- |
|Phase 1 | ソースインボイスの構文から汎用Structured CSVを作成します。 | 入力はPeppol UBL InvoiceXMLで始まります。 ソース 構文バインディング マップ インボイス 共通への事実 EN 16931 / UADC 階層 Structured CSV. 同じフェーズはxBRL-CSVメタデータJSONを記述し、生成されたxBRL-CSVタクソノミに対してジェネリック表現を検証します。 お問い合わせ**PoCベースラインの完成**Peppol UBL入力, Structured CSV 生成, メタデータ JSON 生成, タクソノミ とメタデータ検証, UBL 往復スキーマチェック機能. お問い合わせ
|Phase 2 | 汎用Structured CSVを目的に換算します。 | 現在の目標は6つのADS XBRL GLビュー、6 ADS PSVビュー、ISO 21378:2019 ADCテーブル38、39、53、および54 CSVビューです。 |**計画されたPoC 適用範囲 のために完了します。**ターゲットバインディング、生成、回帰テスト、およびISOマッピングギャップを文書化しました。 |
|フェーズ3 | サポートされている入力構文と相互運用性テストを展開します。 | UN/CEFACT インボイス および XBRL GL インボイス Peppol UBL とともに、追加のソース入力として例を追加します。 Peppol インボイス、 UN/CEFACT インボイス、 XBRL GL インボイス に対応する出力変換を追加します。 | 今後の方向性 フィンランドとエストニアで議論されているプロファイルはXBRL GLが含まれています。 |

Phase 1 は、中立的な中間表現に意図的に焦点を合わせます: 検証され、往復できる汎用的で階層的な Structured CSV。 Phase 2 は、複数の下流フォーマットのソースとして一般的な表現を使用します。 この分離は、コアUADCの考え方です。入力構文変換は、ターゲットフォーマットの投影から分離されます。

## 処理の流れ

```
Phase 1 source syntax conversion
  Peppol UBL Invoice XML
  future: UN/CEFACT Invoice, XBRL GL invoice
    -> syntax binding
    -> generic EN 16931 / UADC Structured CSV
    -> xBRL-CSV metadata JSON
    -> taxonomy and metadata validation
    -> round-trip validation back to source syntax where supported

Phase 2 target-format projection
  generic EN 16931 / UADC Structured CSV
    -> ADS XBRL GL syntax binding
       -> Invoices Received/Generated and Lines
       -> Supplier Listing and Customer Master
    -> ADS semantic binding
       -> ADS O2C/P2P PSV views
    -> ISO 21378 semantic binding
       -> ADC Tables 38, 39, 53, and 54 CSV views

Future additional target projections
    -> Peppol Invoice
    -> UN/CEFACT Invoice
    -> other XBRL GL invoice profiles

Later interoperability tests
  -> XBRL GL invoice examples and profiles
  -> Finland and Estonia XBRL GL discussion targets
```

## ディレクトリレイアウト

- **ドキュメント/**- 人読み可能なプロジェクト文書。 まずは**docs/README.md**.
観音ガイドは**SETUP.md**, **TUTORIAL.md**, **SYNTAX_BINDING.md**, **SEMANTIC_BINDING.md**と**DATA_MODEL.md**. 建築の決定履歴は残っています**docs/decisions/**.
- **参考文献/**- 外部ソースのメモと標準、ソースの仕様、および実装の参照を解釈するために使用されるリンク。 リポジトリの外で大規模なライセンスされたソース文書を保持し、ここに再現可能なメモやポインタのみを記録します。
- **specs/lhm/**- LHM/HMD EN 16931 インボイス PoC. generated/current CSVはここに保存されますが、**specs/lhm/source/**LHM を再生または調整するために使用される編集可能なソース CSV を保持します。 ローカルレビュアーワークブックはGitで無視されます。
- **specs/bindings/**- バイナリ定義。 アクティブ UBL Invoice 構文バインディング は、**specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv**; LHM 意味パス を UBL XPath 式と selector 前方および逆変換で使用される述語にマップします。 Phase 2 ADS XBRL GL 結合 CSV ファイルが下にあります。**specs/bindings/syntax/**. レビューワークブックは**specs/bindings/ADS_XBRL_GL_Bindings.xlsx**. ADS PSV および ISO 21378 ADC CSV の結合は下にあります**specs/bindings/semantic/**.
- **samples/input/**- ベースラインチェックにコミットした小サンプル入力ファイル(最小UBL Invoice)のサンプルと選択されたBIS Billing例インボイスs。
- **samples/expected/**- 軽量回帰チェックの予想される出力は、安定した予想されるアーティファクトが便利です。
- **ログイン**- 運用変換スクリプトと初心者のチュートリアルラッパー。 お問い合わせ
**src/README.md**そして、**src/tutorial/README.md**.
- **テスト/テスト**- 回帰チェックと生成された往復レビューアーティファクト。 お問い合わせ
**tests/README.md**.
- **ツール/**- 初期設定、支持生成、環境維持、
開発ヘルパーツール お問い合わせ**tools/README.md**, **tools/taxonomy/README.md**と**tools/tutorial/README.md**. 全15個のツールが指定されています。**docs/DATA_MODEL.md**.
- **アウト/**- Git によって追跡される PoC の証拠およびターゲット出力を発生させました。 タクソノミ 出力、Structured CSV 出力、逆変換出力、Phase 2 対象ビュー 、および選択されたレンダリングされた文書 QA のアーティファクト。 これらのファイルを直接編集するのではなく、ソース定義から再生します。
- [**XBRL_GL_Next_UADC_PoC.pdf**](../XBRL_GL_Next_UADC_PoC.pdf) - UADCのプロジェクト概要文書 ポック
そしてその関係 XBRL GL 次へ。

タクソノミ 発電機は、**tools/taxonomy/xBRLGL_TaxonomyGenerator.py**. 生成された xBRL-CSV タクソノミ エントリ ポイントは**out/taxonomy/plt/en16931-oim-2026-07-05.xsd**そして、そのディメンションal 定義リンクベースは**out/taxonomy/plt/en16931-def-2026-07-05.xml**. エントリーポイントは EN 16931 表示リンクベース を発見するので、Arelle は LHM 階層を表示します。 Tuple/content タクソノミ などのスキーマ**plt-all-<version>.xsd**そして、**en16931-content-<version>.xsd**このPoCでは生成されません。

## 現在の 適用範囲

1. EN 16931 インボイス LHM を汎用 Structured CSV で定義し、監査します。
2. Peppol UBL Invoice XML を汎用 UADC Structured CSV に変換します。
3. 参照するxBRL-CSVメタデータを生成します**en16931-oimの**タクソノミ エントリーポイント。
4. 生成された xBRL-CSV メタデータを Arelle で検証します。
5. Structured CSV から UBL Invoice XML を再構築し、UBL 2.1 スキーマで検証します。
6. Phase 2 ADS XBRL GL 対象ビュー を Phase 1 Structured CSV から生成します。 現在のADS XBRL GL出力は下書きされます**out/phase2/ADS_XBRL_GL/<構造化されたcsv-stem>/**として**Invoices_Received.xbrl**, **Invoices_Generated.xbrl**, **Invoices_Received_Lines.xbrl**, **Invoices_Generated_Lines.xbrl**, **Supplier_Listing.xbrl**と**Customer_Master.xbrl**.
7. Phase 2 ADS PSV のビューを生成します。**out/phase2/ADS_PSV/**と ISO 21378 ADC インボイス 下のCSVビュー**out/phase2/ISO21378_ADC/**.
8. OpenPeppol BIS Billing ベースライン上に最初の CIUS/profile 層として EN 16931 を保持します。
9. UN/CEFACT インボイス および XBRL GL インボイス を含む追加のソース入力およびターゲットプロファイルのための次のフェーズ デザインを用意します。

## タスク

1. ジェネリック Structured CSV の LHM を定義します。 LHM は EN 16931 インボイス 階層としてビジネス用語を説明しています。 意味パスs、有効**lhm  レベル**値、および 構文バインディング 参照。 最初の構文バインディングは、このニュートラルStructured CSV表現にPeppol UBL InvoiceXMLをマップします。

2. xBRL-CSV タクソノミ を LHM に定義します。 タクソノミ ジェネレータは LHM CSV を読み込み、EN 16931 モジュールスキーマを出力します。**en16931-oimの**エントリーポイント,**en16931-defの**ディメンションal 定義リンクベース, ラベル, 表示リンクベース. Hypercubes、ディメンション、プライマリアイテム、およびプレゼンテーションの親子関係は、効果的なLHM階層から派生しています。 Class/BG プレゼンテーションノードは OIM のプライマリアイテムを使用します。 BT/fact ノードはモジュールの概念を使用します。 生成された タクソノミ は Arelle でチェックされます。**out/taxonomy/plt/en16931-oim-2026-07-05.xsd**エントリーポイントとして。

3. XML インスタンスを JSON メタデータで構造化した CSV に変換します。 構文バインディング コンバーターは Peppol UBL Invoice XML インスタンスを読み込み、 LHM XPath 結合を適用し、階層 Structured CSV を書きます。 同時に、CSVディメンションと生成されたタクソノミに事実の列をリンクするxBRL-CSVJSONメタデータを書きます。 JSON メタデータを Arelle で検証します。**loadFromOIM から**.

4. ラウンドトリップ 構造化された CSV から XML インスタンスへの変換を実行します。 リバースコンバージョンは、構造化されたCSVと同じLHM/syntaxのバインディング定義を読み、UBL InvoiceXMLインスタンスを再構築し、UBLスキーマのバリデーションに必要な必要な構文サポート値を追加します。 絶対結合 XPath は、繰り返されたセマンティックコンテクストの外側を指すと UBL 文書に根ざしたままである。例えば、 BT-90 は、支払いの指示下にあるが、書き込みは**アカウンティングサプライヤーパーティー**以下**支払方法**. その結果、XML は、XML パーサと UBL 2.1 スキーマの検証でチェックされます。

5. Peppol UBLのベースラインが安定した後、追加の入力構文esを追加します。 計画されたソース入力には、UN/CEFACT インボイス と XBRL GL インボイス の例が含まれます。 これらは同じジェネリックStructured CSVにマップする必要があります。

6. 計画されたPhase 2をジェネリックStructured CSVからターゲット予測を完了します。 ADS O2C/P2P XBRL GLおよびPSV結合およびISO 21378:2019 ADC 表38、39、53、および54 CSVの結合は定義され、テストされます。 サプライヤーリストの場所 売り手 郵便住所の下**識別子Type=V**識別子の参照。 ISOの結合は、直接マッピング、顕著な近似、必要な変換、およびEN 16931からのデータの不在を特定します。 これは、PoC 適用範囲 の Phase 2 を完了します。 EN 16931 単独で ISO 21378 監査フィールドをすべて供給することを主張しません。

結果のアーティファクトは、XML 解析と UBL スキーマ検証で再現された状態で、xBRL-CSV レポートと タクソノミ の 2 つのレベルでチェックされます。

## 現在のテスト

```
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
& $python .\tests\validate_taxonomy.py
& $python .\tests\test_openpeppol_invoice_conversion.py
& $python .\tests\test_bis_billing3_examples_conversion.py
& $python .\tests\test_roundtrip_artifacts.py
& $python .\tests\test_xbrl_csv_metadata_arelle.py
& $python .\tests\test_ads_invoices_received_xbrl_gl.py
& $python .\tests\test_ads_invoices_generated_xbrl_gl.py
& $python .\tests\test_ads_invoices_received_lines_xbrl_gl.py
& $python .\tests\test_ads_invoices_generated_lines_xbrl_gl.py
& $python .\tests\test_ads_supplier_listing_xbrl_gl.py
& $python .\tests\test_ads_customer_master_xbrl_gl.py
```

サンプル UBL Invoice XML と BIS の課金例が変換されます。**specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv**. EN 16931 変換ベースラインが安定した後に OpenPeppol CIUS チェックが追加されます。

意味パス 要素はビジネス利用規約から生成されます**downCamelCaseConcatenatedの特長**例えば:

```
Invoice issue date -> invoiceIssueDate
Seller postal address -> sellerPostalAddress
```
