# Phase 1 構文バインディング

## コンテンツの表

1. 目的
2. 主なプログラム
3. 入力ファイル
4. フォワード出力
5. 逆出力
6. コマンドラインインターフェイス
7. フォワード 処理モデル
8. メタデータ JSON 処理モデル
9. 逆 処理モデル
10. 通貨属性のルール
11. 制約
12. 回帰テスト
13. 非目標
14. 運用ワークフロー
15. 機能レベルの処理の参照
16. 構文バインディング 変換の概要
17. 構文バインディング 利用者ガイド

## 1. 目的

このドキュメントでは、構文バインディングの変換プログラムをUADCの概念の証明で指定します。

プログラムは、XML インボイス ドキュメントを ディメンション ベースの階層 CSV に変換し、構文バインディング CSV. 転送変換中に、CSV 列を生成した タクソノミ に関連付ける JSON メタデータも書き込みます。 また、同じバインディング情報でXMLに戻る階層CSVをXMLに戻すことができます。

実装レベルの処理の詳細は、この文書の第7章～10章および第15章に含まれています。

この文書のすべてのパスは、**UADC ポック**リポジトリの後に作業ディレクトリが押し込まれたりクローン化したりします。ただし、先頭のパスを除く**../**兄弟のディレクトリを参照する**UADC ポック**.

## 2. 主なプログラム

プログラム:

```
src/syntax_binding.py
```

コンバータは、サポートされている名前空間とXPathヘルパー関数が、運用階層コンバーターによって使用されます。

## 3. 入力ファイル

### 3.1 XML入力

XML 入力は UBL Invoice XML ドキュメントです。

PoCのサンプル:

```
samples/input/openpeppol_ubl_invoice_minimal.xml
```

パッケージのサンプル:

```
../syntax_binding_revised_package/invoice.xml
```

### 3.2 構文バインディング CSV

結合CSVは、セマンティックモデルパスをXMLXPath式にマップします。

PoCの結合:

```
specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv
```

パッケージの結合:

```
../syntax_binding_revised_package/bindings.csv
```

必要な操作の結合のコラム:

```
sequence
level
structured_csv_level
type
name
datatype
multiplicity
semantic_path
structured_csv_column
element
xpath
```

両方の列なし**semantic_path**そして、**xpathの**事実抽出のために無視されます。**タイプ=C**rows はセマンティッククラスのコンテキストを定義し、行スコープs を繰り返します。**タイプ=A**rows は、抽出可能な値または遺伝子変数値を定義します。

### 3.3 結合埋め込まれた LHM レイアウト

構文バインディング CSV は、必要な LHM 列をコピーし、LHM 行の順序を予約することによって定義されます。 したがって、コンバータはバインディング表自体を使用して定義します。

- 出力列の順序;
- BG ディメンション列s;
- BT 値の列;
- 意味パスから最終LHMまでのマッピング**エレメント**名前;
- BGを繰り返す**multiplicity**;
- 利用可能なBG行のコンテキストXPathを繰り返します。

LHM ソースは、これらの列のガバナンス・ソースのままです。

```
specs/lhm/EN16931_CIUS_Invoice_LHM.csv
```

### 3.4 テンプレート CSV

いつか**--template-csv**変換器は、そのヘッダーを出力列の順序として使用し、非空のテンプレート行からフィールドツーディメンション配置を誘導します。

パッケージテンプレート:

```
../syntax_binding_revised_package/invoice.csv
```

お問い合わせ**--template-csv**供給されると、結合由来のレイアウトはメインフィールドの順番を制御し、テンプレートはフィールド配置のヒントを提供できます。

## 4. フォワード出力

出力はUTF-8-SIG CSVファイルです。

PoCの出力:

```
out/phase1/openpeppol_ubl_invoice_minimal.csv
```

パッケージの出力:

```
out/phase1/<input-xml-stem>.csv
```

出力には以下が含まれます。

- **dInvoice**ルートとして ディメンション列;
- 追加情報**d***BGを繰り返すためのカラム。
- ディメンション列sの後のBTの価値コラム;
- インボイスレベルの事実のための1つのルート行;
- 結合が価値を作り出すBGのコンテキスト1列。

フォワード変換もJSONメタデータを書きます。 デフォルトでは、メタデータファイル名は次のようになります。

```
<output-csv-stem>.json
```

例えば:

```
out/phase1/openpeppol_ubl_invoice_minimal.json
```

メタデータは xBRL-CSV メタデータ ドキュメントで Arelle を読み込みます。**loadFromOIM から**プラグイン。 構造化されたCSVテーブルを生成したxBRL-CSVタクソノミエントリポイントにリンクし、CSV列をタクソノミコンセプトにマップします。 レポート**ドキュメント情報タクソノミ**プロパティは空でなければなりません。**en16931-oimの**変換エラーとして扱われます。 JSONメタデータ名 xBRL-CSV OIM タクソノミ エントリーポイント**out/taxonomy/plt/en16931-oim-<version>.xsd**.

## 5. 逆の出力

いつか**--reverse**入力は階層 CSV で、出力は XML ファイルです。

逆出力例:

```
out/reverse/en16931_reverse_invoice.xml
```

逆のコンバーター:

- 階層 CSV 列を読み込みます。
- 構文バインディング CSV を介してフィールドを解決します。
- ディメンション 行でフィールドを関連付けるために、バインディング デリブ レイアウトを使用します。
- UBL Invoice XML 要素をバインド XPath 式から作成します。
- 境界値を持つ各繰り返し ディメンション 行ごとに 1 つの XML コンテキストを作成します。
- 必要な導体**通貨ID**インボイス 通貨フィールドから要素を量る属性。
- 意味が 反復クラス に属している場合でも、文書で根ざした XPath のコンテキストをそのまま保持します。
- 下記のBT-90を書いて下さい**アカウンティングサプライヤーパーティー**ネストされたものを決して作りません**インボイス**お問い合わせ**支払方法**.

## 6. コマンドラインインターフェイス

```
syntax_binding.py XML_FILE -b BINDING_CSV -o OUTPUT_CSV [options]
```

逆の形態:

```
syntax_binding.py INPUT_CSV --reverse -b BINDING_CSV -o OUTPUT_XML [options]
```

引数:

- **XML FILEの使い方**: 転送モードにXMLファイルを入力します。
- **インプット CSV**: リバースモードで階層 CSV ファイルを入力します。
- **-bの**, **--binding**: 構文バインディング CSV.
- **ツイート**, **--output**: 前方モードの階層 CSV を出力するか、逆モードの XML を出力します。
- **--template-csv**: 列順とディメンション配置を定義するオプションのCSVテンプレート。
- **--metadata-output**: 任意JSONメタデータ出力パス。 デフォルトは出力CSVパスです。**.jsonの**拡張子。
- **--taxonomy-base**: 生成された タクソノミ JSON メタデータで参照されるベースディレクトリ。 デフォルトは**out/taxonomy**.
- **--reverse**: 階層 CSV を XML に変換します。
- **--drop-empty-columns**: 生成された行に値がない列を削除します。
- **--d-invoice**: に書かれている値**dInvoice**カラム。 デフォルトは**1**.
- **ツイート**, **--encoding**: CSVエンコーディング デフォルトは**utf-8シグ**.

## 7. フォワード 処理モデル

### 7.1 名前空間の処理

コンバーターは入力XMLからXML名空間宣言を収集します。**xml.etree.ElementTree.iterparse は、**.

XPathヘルパー関数は、以下のような名前空間プレフィックスされた要素をサポートしています。

```
/Invoice/cbc:ID
/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name
```

### 7.2 結合埋め込まれた LHM レイアウトのローディング

構文バインディングテーブルが読み込まれるとき:

1. C行はBG/class行として扱われます。
2. C 行は インボイス の root か multiplicity が繰り返される場合にのみ ディメンション になります。**0..***または**1..***.
3. BG 行の非依存化は、セマンティック・グループ化ノードのままであり、ディメンション として生成されません。
4. ディメンション として生成される名前**ログイン**+ アッパーキャメルケース**エレメント**).
5. 行はBT/fact行として扱われます。
6. ファクトカラム名は、**構造 csv column**.
7. 各事実は最も近い祖先に繰り返されるディメンションに割り当てられます。

multiplicity を繰り返すと、上部の境界が検出されます。

```
*
n
unbounded
```

数値の値よりも大きい**1**.

### 7.3 結合解析

各結合行は、内部結合レコードに変換されます。

```
semantic_path
xpath
root
dimension
filter_field
filter_value
field
```

コンバーターは支えます:

- ルートレベルのパスなど**$.invoice.invoiceNumber**;
- ディメンション オプションのフィルタ述語でパス;
- 一般的なネスト 意味パス は、最も近い LHM ディメンション で解決しました。

### 7.4 列生成

フォワード変換は、繰り返しグループを独自に処理するのではなく、XMLの親コンテキスト再帰を使用します。 コンバーターは作成します:

- ルート インボイス 行 インボイス レベルの事実;
- 反復された BG 行は、VAT の故障や インボイス 行などの繰り返しコンテキストを行ないます。

繰り返しBG行の場合:

1. コンバーターはビルドします。**ビンディングクラス**ツリーから**タイプ=C**行。
2. ルートコールが始まります**dInvoice=1**.
3. 現在のクラスについては、直接**タイプ=A**現在のXML文脈に相対的にXPathで事実を抽出します。
4. 非反復子クラスは現在のStructured CSV行を再利用します。
5. 反復子クラス は、現在の親の XML コンテキストで 1 つの発生時に処理されます。
6. 繰り返された各発生は、次のような1-ベースディメンション値を受け取ります。**dInvoiceLine=2**.
7. Ancestor は ディメンション 値がネストされた繰り返し行にコピーされます。

未就学児クラスは親行に平坦化されます。 繰り返す子クラスは平坦化されていません: その最初とその後の発生は、別々の子行に書かれています。 例えば:

```csv
dAaa,dBbb,a1,a2,b1,b2,b3
1,,a1V1,a2V1,,,
1,1,,,b1V1,b2V1,b3V1
1,2,,,b1V2,b2V2,b3V2
```

したがって、親行は空**b1の**, **b2**と**b3**フィールド。 のような行**1、a1V1、a2V1、b1V1、b2V1、b3V1**保有する事実をミックスするので、無効です**dAaa**繰り返すことによって所有される事実を使って**dBbb**適用範囲.

### 7.5 コラムの処理

LHM が使われている場合は、フィールドの順番は次のとおりです。

```
dimension columns first, then fact columns
```

LHM なしでテンプレートを使用する場合、テンプレートヘッダーは出力順を制御します。

LHM もテンプレートもヘッダを提供していない場合、フィールド名はバインディングから派生します。

## 8. メタデータ JSON 処理モデル

転送モードでは、構造化されたCSVが生成された後、コンバータはJSONメタデータを書き込みます。

メタデータ構造はxBRL-CSVのレポートパッケージ形状に従います。

- **ドキュメント情報**: xBRL-CSV ドキュメントタイプ、名前空間、および タクソノミ エントリーポイント参照。
- **テーブル**: 生成された構造化されたCSVテーブルとその相対URL。
- **テーブルテンプレート**:テーブルレベルのディメンションとパーカラムの概念マッピング。

ディメンション列 はテーブル ディメンション として宣言されます。

```
"plt:d_en16931_Invoice": "$dInvoice"
```

Fact カラムは xBRL コンセプトで宣言されます。

例:

```
{
  "InvoiceNumber": {
    "dimensions": {
      "concept": "en16931:InvoiceNumber"
    }
  }
}
```

マウント事実は、デフォルトのテストユニットを受け取ります**iso4217:JPY**LHM のデータ型が値を示すときのメタデータ 生産使用は、該当する通貨用語から単位を導き出す必要があります。

## 9. 逆 処理モデル

逆モード:

1. コンバーターは入力階層 CSV を読みます**ログイン ディクトリーダー**.
2. コンバーターは、バインディング デリブ レイアウトとバインディング CSV をフォワード モードと同じ方法で読み込みます。
3. XML作成の前に、各事実は、その行の最も深いポップアップディメンションに対してチェックされます。 祖先ディメンションが所有する事実は、繰り返された子行で拒否されるため、混合されたparent/child行は逆変換できません。
4. ルートレベルのフィールドは、インボイスルートの直下にあるXMLパスに書かれています。
5. ディメンション フィールドをグループ化**d***ディメンション列.
6. 境界値を持つ各ディメンション行に対して、コンバータはBGXPathから繰り返しXMLコンテキストを作成します。
7. 境界フィールドの値は、そのコンテキストの下にある XPath に書かれています。
8. XPath などの述語**cbc:ChargeIndicator=false()**そして、**cbc:DocumentTypeCode='130' の**マッチングXMLコンテキストが作成されると子の値として材料化されます。
9. 量要素が受け取れる**通貨ID**インボイス の文書通貨フィールドから。 税理士法人税理士法人税理士法人税理士法人税理士法人税理士事務所**通貨ID**税務会計の通貨フィールドから。
10. お問い合わせ**相対パス(binding.xpath, Repeat path)**絶対まま、結合は繰り返した構文のコンテキスト外にあり、文書のルートから書かれています。 含まれているパスのみが繰り返された要素に相対的に書かれています。
11. EN 16931 BT でない UBL 必須 対応要素は、スキーマ検証に必要な場所で追加されます。**cac:TaxScheme/cbc: インフォメーション**行方不明**cbc:ChargeIndicator=false(偽)**.
12. 生成された UBL 子要素は UBL スキーマシーケンスに正規化されます。 いつか**--ubl-schema-root**または**--ubl-schema-url**供給される、コンバーターはXSDからの子供の発注を導きます**xs:シーケンス**宣言。 スキーマソースがなければ、サポートされている インボイス 構造の組み込みフォールバック順を使用します。

リバースコンバーターは現在、PoC UBL Invoice の結合パターンを対象としています。 規範的なXML再生ではなく構造化されたCSV表現の往復検証を目的としています。

## 10. 通貨属性規則

構文バインディング は扱います**通貨ID**意味的な通貨条件から派生した構文メタデータとして:

- BT-5**ドキュメント通貨コード**デフォルトは**通貨ID**インボイス の量要素のため。
- BT-6**税務会計通貨コード**です。**通貨ID**税理士法人税理士法人税総支店
- BT-110 および BG-23 UBL パス述語を使用する**cbc:税額/@currencyID=/Invoice/cbc:DocumentCurrencyCode**.
- BT-111 UBLパス述語を使用する**cbc:税額/@currencyID=/Invoice/cbc:TaxCurrencyCode**.

フォワード変換は、これらの絶対述のパスをドキュメントルートから評価します。 お問い合わせ**Allowance-example.xml**, BT-110 が解決する**1225.00 ユーロ**そしてBT-111は解決します**9324.00 SEKの**.

BT-90 クロス適用範囲 リバースマッピング その 意味パス は instructions/direct のデビットの下にありますが、その UBL XPath ポイントは**/Invoice/cac:AccountingSupplierParty/.../cbc:ID**. 逆変換 したがって、 XPath 文書のルートをではなく、構築し続ける**PaymentMeans/Invoice/AccountingSupplierParty**.

したがって、CSV は、意味値と通貨コード値を別々に格納します。 逆変換は必要なUBLを書きます**通貨ID**属性。

## 11. 制約

- コンバーターは内部でUBLスキーマに対してXMLを検証しません。 回帰テスト**tests/test_roundtrip_xml_ubl_schema.py**UBL 2.1スキーマ検証を実行します。
- コンバーターはEN 16931ビジネスルールを検証しません。
- コンバーターは内部でArelleを実行しません。 回帰テスト**tests/test_xbrl_csv_metadata_arelle.py**Arelle で生成されたメタデータを検証します。
- コンバータは、完全な評価しません XPath 2.0.
- サポートされている述語は、PoC 結合で使用されるケースに意図的に制限されます。
- テンプレートの列だけは行を作成しません。行は一致の結合を必要とします。
- 逆のXML要素の順序は供給されたUBL XSDのスキーマの根かUBL InvoiceスキーマのURLから派生することができます。 組み込みのチャイルドテーブル**syntax_binding.py**スキーマソースが供給されていない場合のフォールバックのみです。
- リバースXMLは、アンバウンドXMLコンテンツを省略できます。
- リバースXMLは、CSV値の境界から生成され、XMLと同じバイトバイト単位であることは意図されていません。

## 12. 回帰テスト

PoC LHM 主導変換テスト:

```
tests/test_lhm_hierarchical_csv_layout.py
```

パッケージtemplate/binding変換テスト:

```
tests/test_syntax_binding.py
```

OpenPeppol 構造変換テスト:

```
tests/test_openpeppol_invoice_conversion.py
```

逆変換の往復テスト:

```
tests/test_syntax_binding_reverse.py
```

ラウンドトリップアーティファクトとメタデータテスト:

```
tests/test_roundtrip_artifacts.py
```

## 13. 非目標

構文バインディング コンバーターは使用しません:

- LHM の定義を生成します。
- XBRL タクソノミ ファイルを生成します。
- フラットCSVに意味バインディングを実行します。
- 完全な EN 16931 または OpenPeppol 検証を実行します。
- リポジトリの同期や出版物を実行します。

## 14. 運用ワークフロー

### 14.1 準備 Phase 1 入力

設定された入力ディレクトリに UBL インボイス を置き、マッチングの構文結合 CSV を選択します。 行を結合する**タイプ=C**クラスツリーを定義する; 行と**タイプ=A**事実抽出と逆書きルールを定義します。 テーブルがランタイム権限であるため、処理前のバインディングバージョンを確認します。

### 14.2 変換とインスペクト

ログイン**src/syntax_binding.py**1つのXML文書または入力ディレクトリ。 生成された Structured CSV をスパース親と繰り返し子行の タクソノミ エントリ ポイント、 ディメンション、および単位の JSON メタデータを検査します。 第4章 の**DATA_MODEL.md**必要な行パターンを定義します。

### 14.3 リバースと検証

UBLを再構築するために逆モードを使用して下さい。 コンバーターはドキュメントのルートから始まり、スキーマの順序で絶対XPathの祖先を作成し、述語と通貨属性を適用し、空の小数要素を省略します。 結果のXMLをUBLスキーマで検証し、元のStructured CSVで2番目の転送変換を比較します。

## 15. 機能レベルの処理の参照

### 15.1 結合およびレイアウトのローディング

- **読み込み binding rows**行の注文を失うことなく、結合CSVを読みます。
- **build layout from rows をビルドする**derives 列, ディメンション 所有権, クラス
multiplicity、および結合埋め込まれたLHMレイアウト。
- **read bindings ディレクティブ**属性行を結合オブジェクトに変換し、解決します
意味パスs.
- **build binding class tree をビルドする**両方のネストされたクラスモデルをビルド
方向。
- **直接 class fields**そして、**Walk binding classes ディレクティブ**と事実を関連付ける
自分自身のクラスと、それを決定的に横断します。

### 15.2 XPath 評価

- **Collect namespaces は、**入力XMLで宣言されたレコード名空間。
- **xml split xpath は、**, **xml split step predicate は、**と
**xml split terminal attribute ディレクティブ**安全に結合XPathを分解します。
- **検索ノード**, **xml predicate matches ディレクティブ**と**get value を使う**評価 XPath
既定のクラスのコンテキストに相対して、文書のルート参照を述語で許可します。
- **infer repeat path ディレクティブ**, **common xpath prefix ディレクティブ**と**相対パス**デリブ
反復クラスのXMLノード適用範囲。

### 15.3 行の排出を進む

- **write hierarchical csv ディレクトリ**オーケストラは再帰的XMLトラバーサル、 ディメンション
数値化、疎な行 排出量、列順化、メタデータ作成。
- **新規登録**ancestor ディメンション で行を作成します。
- **row has values ディレクティブ**構造的に出力行を空にします。
- **validate hierarchical row 適用範囲s は、**繰り返された子供の最初の値を拒否する
親行にマージされたとき。
- **drop empty カラム**未使用の値の列を削除し、必要に応じて保存します
ディメンション.

単一の子にとって、抽出されたフィールドは最も近い繰り返し祖先の列に残ります。 繰り返された子のために、親行は別々に排出され、各子はそれぞれディメンション行に発生します。

### 15.4メタデータ生成

- **バインディング column metadata**導体コンセプト、データ型、ディメンション、ユニット
結合からの情報。
- **タクソノミ エントリーポイント**タクソノミ エントリ ポイントを選択します。
- **xbrl csv column 定義**OIM 互換カラム定義を作成します。
- **write csv メタデータ**JSONメタデータと相対テーブルパスを記述します。

### 15.5 逆 XML の構造

- **write xml from hierarchical csv を記述**ディメンション 適用範囲 のグループ行とドライブ
XML再構築。
- **スプリット xml path**, **セキュアパス**と**find or create child の一覧**プロセス
UBLのルートから絶対XPath;彼らは一致の子孫のために世界的に検索しません。
- **set xml value ディレクティブ**, **set relative xml value ディレクティブ**と
**set xml value with currency ディレクティブ**非空のソース値が存在する場合にのみ値を書き込みます。
- **application currency 属性**そして、**resolve currency references は、**シェア
条件付き額の税理士通貨からの文書通貨。
- **load ubl child order の一覧**そして、**sort children for ubl schema をソート**配置要素
シリアル化前の UBL スキーマシーケンス

### 15.6 検証境界

コンバータは階層の行契約を検証し、スキーマ形状のXMLを再構築しますが、外部のUBLスキーマ検証は必要なテストステップのままです。 EN 16931 や Peppol Schematron などのビジネスルールの検証はコンバーターの外にあり、周囲のワークフローで実行する必要があります。


## 16. 構文バインディング 変換の概要

### 構文バインディング 変換 文書

このディレクトリは、XML-to-structord-CSVと構造化されたCSV-to-XML変換プログラムを文書化します。

XPath コンテキスト処理の詳細な実装レベルの説明については、意味パス 解像度、**dInvoice**そして、**dInvoiceLine**ディメンション 取扱い、内部**dict/list/dataclass**オブジェクト、関数レベルのデータフロー、使用**DATA_MODEL.md**, 第15章. このドキュメントは プログラム仕様書 で、シンタックスバインドコマンドのガイドを操作します。

#### ファイル

- **program_specification.md**- コンバーターの入力、出力、ディメンションの動作、JSONメタデータ生成、リバース変換、通貨処理、XPathの処理、および非目標を定義します。
- **user_guide.md**- 前方変換、逆変換、往復アーティファクト、トラブルシューティングのコマンド例を説明します。

#### 関連ディレクトリ

- **../../src/**- コンバーターの実装、特に**syntax_binding.py**.
- **../../specs/bindings/syntax/**- アクティブ UBL Invoice 構文バインディング CSV.
- **../../specs/lhm/**- LHM 構造化されたCSV列とタクソノミの概念を定義するために使用されるCSV。
- **../../tests/roundtrip/**- 見直し可能なソースXML、構造 CSV、メタデータJSON、および再生XMLアーティファクト。

Phase 1 安定ベースラインとして EN 16931 構文バインディング を使用します。 OpenPeppol CIUS のチェックは後続のオーバーレイとして計画されます。



## 17. 構文バインディング 利用者ガイド

### 利用者ガイド: 構文バインディング XML-to-階層-CSV コンバージョン

#### 1. 働くディレクトリ

コマンドを実行する**UADC ポック**ディレクトリ:

```
cd UADC_PoC
```

以下のすべてのパスは、最初から始まる場合を除き、このディレクトリに相対的です。**../**.

ローカルWindows環境用のPythonコマンドを設定します。

```
$python = 'python'
```

#### 2. 主なスクリプト

使用:

```
src/syntax_binding.py
```

このスクリプトは、XML を ディメンション ベースの階層 CSV に 構文バインディング CSV に変換します。 また、階層 CSV から XML への逆変換にも対応しています。**--reverse**.

XPath の親コンテキスト再帰、意味パス の解像度を含む実装の詳細は、**dInvoice**そして、**dInvoiceLine**割り当て、機能レベルのデータフロー、参照**DATA_MODEL.md**, 第15章.

#### 3. PoC OpenPeppol サンプルを変換

実行:

```
& $python .\src\syntax_binding.py `
  .\samples\input\openpeppol_ubl_invoice_minimal.xml `
  -b .\specs\bindings\syntax\EN16931_UBL_Invoice_Syntax_Binding.csv `
  --metadata-output .\out\phase1\openpeppol_ubl_invoice_minimal.json `
  --taxonomy-base .\out\taxonomy `
  -o .\out\phase1\openpeppol_ubl_invoice_minimal.csv
```

出力:

```
out/phase1/openpeppol_ubl_invoice_minimal.csv
out/phase1/openpeppol_ubl_invoice_minimal.json
```

このコマンドは、構文バインディングに埋め込まれたLHM由来の列を使用して、出力ディメンションと実際の列を決定します。 CSV 列を生成した タクソノミ に関連付ける JSON メタデータも作成します。

コンバーターは扱います**lhm  レベル**Structured CSV の有効な階層として。 ブランク付きBG行**lhm  レベル**、非反復売り手や買い手などのグループは、セマンティックグループ化ノードのみです。 BT値は、最寄りの祖先ディメンション行に書かれています。

#### 4. 改訂されたパッケージのサンプルを転換して下さい

実行:

```
& $python .\src\syntax_binding.py `
  ..\syntax_binding_revised_package\invoice.xml `
  -b ..\syntax_binding_revised_package\bindings.csv `
  --template-csv ..\syntax_binding_revised_package\invoice.csv `
  --metadata-output .\out\phase1\package_invoice_hierarchical.json `
  -o .\out\phase1\package_invoice_hierarchical.csv
```

出力:

```
out/phase1/package_invoice_hierarchical.csv
out/phase1/package_invoice_hierarchical.json
```

このコマンドは、パッケージテンプレート CSV を使用して、予想される出力列の順序を保存します。

#### 5. コマンドオプション

基本フォーム:

```
& $python .\src\syntax_binding.py XML_FILE `
  -b BINDING_CSV `
  -o OUTPUT_CSV
```

オプション:

- **--template-csv**: テンプレート CSV ヘッダを使用して、出力列順を定義します。
- **--metadata-output**: JSON メタデータ出力パスを設定します。 デフォルトは出力CSVパスです。**.jsonの**拡張子。
- **--taxonomy-base**: JSON メタデータで参照される生成された タクソノミ ディレクトリを設定します。 デフォルトは**out/taxonomy**.
- **--reverse**: 階層 CSV を XML に変換します。
- **--ubl-schema-root**: UBL XSDファイルを含むローカルディレクトリ 逆モードでは、子要素の順序はXSDから派生します**xs:シーケンス**宣言。
- **--ubl-schema-url**: UBL Invoice XSD URL. 逆モードでは、インポートされたスキーマは、このURLと子要素の注文から続くXSDから派生しています**xs:シーケンス**宣言。
- **--drop-empty-columns**: 値を持たない出力カラムを削除します。
- **--d-invoice**: 設定**dInvoice**値。 デフォルトは**1**.
- **ツイート**, **--encoding**: CSVエンコーディング デフォルトは**utf-8シグ**.

#### 6. 階層CSVをXMLに逆転させる

まず階層CSVを作成または確認します。

```
& $python .\src\syntax_binding.py `
  .\samples\input\openpeppol_ubl_invoice_minimal.xml `
  -b .\specs\bindings\syntax\EN16931_UBL_Invoice_Syntax_Binding.csv `
  --metadata-output .\out\phase1\openpeppol_ubl_invoice_minimal.json `
  -o .\out\phase1\openpeppol_ubl_invoice_minimal.csv
```

それからそれをXMLに逆にして下さい:

```
& $python .\src\syntax_binding.py `
  .\out\phase1\openpeppol_ubl_invoice_minimal.csv `
  --reverse `
  -b .\specs\bindings\syntax\EN16931_UBL_Invoice_Syntax_Binding.csv `
  -o .\out\reverse\en16931_reverse_invoice.xml
```

出力:

```
out/reverse/en16931_reverse_invoice.xml
```

ローカルの UBL スキーマパッケージから派生する子要素の順序に、加えて下さい**--ubl-schema-root**:

```
& $python .\src\syntax_binding.py `
  .\out\phase1\openpeppol_ubl_invoice_minimal.csv `
  --reverse `
  -b .\specs\bindings\syntax\EN16931_UBL_Invoice_Syntax_Binding.csv `
  --ubl-schema-root .\out\cache\UBL-2.1\xsd `
  -o .\out\reverse\en16931_reverse_invoice.xml
```

オンラインUBL Invoiceスキーマエントリポイントから子要素の順序を導き出すには、**--ubl-schema-url**. コンバーターは、その URL からインポートおよび含まれているスキーマに従います。

CSV値の境界からXMLが生成されます。 往復検証を目的とし、アンバウンドXMLコンテンツを再現しない場合があります。 LHM のとき**シンタックスシーケンス**値、逆出力は UBL スキーマの順序に従うのにそれらを使用します。

株式について**通貨ID**逆変換中に属性が生成されます。

- **ドキュメント通貨コード**通常のインボイスの量要素に使用されます。
- **税務会計通貨コード**税理士法人税理士法人税理士法人税理士法人税理士事務所

為替変換は、これらの通貨条件を使用して、税務総支店を区別します。 インスタグラム**Allowance-example.xml**, BT-110 は、納税額を選択します。**通貨ID**ログイン**ドキュメント通貨コード** (**1225.00 ユーロ**), BT-111 が、税額を選択します。**通貨ID**ログイン**税務会計通貨コード** (**9324.00 SEKの**).

一部の皮脂質の子供は、繰り返された UBL の構文の外に保存されます。 BT-90 は、決済 instructions/direct のデビットに属していますが、 UBL XPath は以下です。**アカウンティングサプライヤーパーティー**. 逆変換中に、現在の繰り返しXPathに含まれていない絶対結合XPathがドキュメントルートから書かれています。 ネストを生成してはならない**インボイス**お問い合わせ**支払方法**.

#### 7.メタデータでテストアーティファクトを生成

往復テストアーティファクトは以下に構築されます。

```
tests/roundtrip/
```

実行:

```
& $python .\tools\build_roundtrip_test_artifacts.py
```

生成されたレイアウトは:

```
tests/roundtrip/<dataset>/
  source_xml/
  structured_csv/
  metadata_json/
  roundtrip_xml/
```

意味:

- **ソース xml**: ソース UBL Invoice XML.
- **構造 csv**: 階層構造 CSV.
- **メタデータ json**: CSV 列の タクソノミ に関する JSON メタデータ。
- **ラウンドトリップ xml**: 構造化されたCSVから再生されるXML。

スクリプトは**--metadata-output**メタデータ JSON を**メタデータ json/**.

#### 8. 入力結合CSV

結合CSVは以下を含むべきです:

```
semantic_path,xpath
```

例:

```
$.invoice.invoiceNumber,/Invoice/cbc:ID
$.invoice.invoiceIssueDate,/Invoice/cbc:IssueDate
```

対応カラムエイリアスも受け付けています。

```
path
source_xpath
xml_path
```

#### 9.出力CSVレイアウト

階層 CSV の使用:

- **dInvoice**インボイス ルートの場合。
- **d***繰り返しBG用カラム ディメンション;
- BT値の事実列。

LHM を使うと、ディメンション列 が最初に配置され、 BT カラムが続きます。

出力パターン例:

```
dInvoice,dVatBreakdown,dInvoiceLine,InvoiceNumber,InvoiceIssueDate,...
1,,,INV-2026-0001,2026-07-06,...
1,1,,,,...
1,,1,,,...
```

親のために**dAaa**そして子供**dBbb**、非尊敬の子供は親行に平らにされます。

```csv
dAaa,dBbb,a1,a2,b1,b2,b3
1,,a1V1,a2V1,b1V1,b2V1,b3V1
```

お問い合わせ**dBbb**繰り返されると、親行はすべての子の事実を空に残し、最初の子の発生は既に別の行にある必要があります。

```csv
dAaa,dBbb,a1,a2,b1,b2,b3
1,,a1V1,a2V1,,,
1,1,,,b1V1,b2V1,b3V1
1,2,,,b1V2,b2V2,b3V2
```

最初の子行に親と反復子の事実を一緒に入れないでください。 逆変換は、その混合行レイアウトのエラーを報告します。

#### 10. JSONメタデータレイアウト

メタデータはxBRL-CSVメタデータドキュメントです。 これらの主要なセクションがあります:

- **ドキュメント情報**: xBRL-CSV ドキュメントタイプと タクソノミ 参照。
- **テーブル**: 生成された構造化されたCSVテーブルURL。
- **テーブルテンプレート**:テーブルレベルのディメンションと実際のコンセプトマッピング。

重要な列が期待通りマップされていることを確認してください。

```
tableTemplates.structured.dimensions["plt:d_en16931_Invoice"] -> "$dInvoice"
tableTemplates.structured.columns.InvoiceNumber.dimensions.concept -> "en16931:InvoiceNumber"
tableTemplates.structured.columns.DocumentCurrencyCode.dimensions.concept -> "en16931:DocumentCurrencyCode"
```

#### 11. 回帰チェック

LHM ドライブされた OpenPeppol サンプル変換チェックを実行します。

```
& $python .\tests\test_lhm_hierarchical_csv_layout.py
```

変更されたパッケージ変換チェックを実行します。

```
& $python .\tests\test_syntax_binding.py
```

OpenPeppol 構造変換チェックを実行します。

```
& $python .\tests\test_openpeppol_invoice_conversion.py
```

逆変換ラウンドトリップチェックを実行します。

```
& $python .\tests\test_syntax_binding_reverse.py
```

往復アーティファクトとメタデータチェックを実行します。

```
& $python .\tests\test_roundtrip_artifacts.py
```

生成された xBRL-CSV メタデータを Arelle で検証します。

```
& $python .\tests\test_xbrl_csv_metadata_arelle.py
```

UBL 2.1 インボイス スキーマに対する再生された往復 XML を検証します。

```
& $python .\tests\test_roundtrip_xml_ubl_schema.py
```

#### 12. トラブルシューティング

##### 利用可能なバインディングが見つかりません

結合CSVが含まれていることを確認してください**semantic_path**そして、**xpathの**値。

##### 出力カラムの欠損

お問い合わせ**--drop-empty-columns**は、生成された値のない列が削除されます。 安定したフルヘッダーが必要な場合は、このオプションなしで実行します。

##### メタデータ JSON は タクソノミ を見つけることができません。

コンバーターは非空文字を書く必要があります**ドキュメント情報タクソノミ**配列。 タクソノミ を最初に生成します。

```
& $python .\tests\test_xbrlgl_generator_uadc_lhm.py
```

またはパス**--taxonomy-base**ディレクトリを含む**plt/en16931-oim-*.xsd**. このスキーマが見つからない場合は、空のタクソノミリストを書く代わりにメタデータ生成が失敗します。

##### 繰り返し行が欠落している

チェック:

- LHMのBG行はmultiplicityなど繰り返しています**0..***または**1..***;
- BG 行は、繰り返し XML コンテキストを指す XPath を持っています。
- 構文バインディング CSV には、その BG 意味パス の下にバインディングが含まれています。

##### ディメンション 行ではなく インボイス ルート行に値が書かれています

構文バインディング CSV に LHM が含まれていることを確認してください。**タイプ:**, **multiplicity**, **semantic_path**と**構造 csv column**カラム。 コンバータは、それぞれBT 意味パスをバインディング表自体から最も近い繰り返しC列ディメンションに解決します。

##### パッケージのサンプル行列は空です

テンプレートの列だけは行を作成しません。 インボイス 行列は インボイス 行の結合を必要とします。

##### 逆XMLは元のファイル注文と一致しません

リバースXMLは、結合行と階層CSV値から再構築されます。 人口 LHM**シンタックスシーケンス**XML要素の順序がチェックされなければならないときのUBLスキーマから。 結合または固定値の規則によって表されるまで、XML コンテンツのアンバウンドはまだ再現できません。
