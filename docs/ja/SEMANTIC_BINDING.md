# Phase 2 意味バインディング

## コンテンツの表

1. 目的
2. 主なプログラム
3. 入力ファイル
4. バインディング表 契約
5. 繰り返し 行スコープ
6. インデックス化された繰り返し値
7. 内部データ構造
8. 加工機能
9. 出力契約
10. 非目標
11. 運用ワークフロー
12. ADS PSV
13. ADS XBRL GL
14. ISO 21378 ADC
15. 機能レベルの処理の参照
16. 検証とトラブルシューティング
17. 意味バインディング 変換の概要
18. 意味バインディング 利用者ガイド
19. ISO 21378 ADC インボイス カバー

## 1. 目的

このドキュメントでは、意味バインディングの変換プログラムをUADCの概念の証明で指定します。

Phase 1 UADC Structured CSV Phase 2 対象となるフラットファイルを 意味バインディング CSV を適用することで変換します。 ターゲットフラットファイルは、PSVまたはコンマ区切りCSVをパイプ分離することができます。 ADS PSV ファイルと ISO 21378 ADC インボイス CSV ファイルは同じ 処理モデル を使用します。

実装レベルの処理の詳細は、この文書の第7章、8章、15節に含まれています。

この文書のすべてのパスは、**UADC ポック**作業ディレクトリ。

## 2. 主なプログラム

プログラム:

```
src/semantic_binding.py
```

コンバーターはXMLの構文とは独立しています。 Structured CSV 行とマップの値を対象列に読み込む**semantic_path**.

## 3. 入力ファイル

### 3.1 Structured CSV 入力

入力はPhase 1 Structured CSVファイルです。**src/syntax_binding.py**.

例:

```
out/phase1/openpeppol_ubl_invoice_minimal.csv
```

入力は複数のStructured CSVファイルを含むディレクトリであってもよい。 その場合、それぞれ**ログイン**ファイルは別々に変換されます。

### 3.2 意味バインディング CSV

意味バインディング CSVファイルが下にある:

```
specs/bindings/semantic/
```

現在の ADS ファイルには以下が含まれます:

```
ADS_Invoices_Received_PSV_Binding.csv
ADS_Invoices_Generated_PSV_Binding.csv
ADS_Invoices_Received_Lines_PSV_Binding.csv
ADS_Invoices_Generated_Lines_PSV_Binding.csv
ADS_Supplier_Listing_PSV_Binding.csv
ADS_Customer_Master_PSV_Binding.csv
```

現在のISO 21378:2019 ADC インボイスファイルは次のとおりです。

```
ISO21378_SAL_Invoice_Generated_CSV_Binding.csv
ISO21378_SAL_Invoice_Generated_Details_CSV_Binding.csv
ISO21378_PUR_Invoice_Received_CSV_Binding.csv
ISO21378_PUR_Invoice_Received_Details_CSV_Binding.csv
```

テーブル 38, 39, 53, 54 からのフラット インボイス ビューを実行します。 TAXグループを繰り返す**税1**コース**税4**カラム。 繰り返されたビジネス部門の値は、**事業紹介 セグメント 01**コース**事業案内 セグメント 05**カラム。 CSV ヘッダが繰り返しフィールド名を含むことができないため、この物理的な拡張が必要です。

## 4. バインディング表 契約

意味バインディングテーブルは、対象の定義テーブルから始まり、UADCマッピングカラムを追加します。

```
field_no,field_name,level,flat_file_data_type,length,description,source_document,semantic_path,type,multiplicity,mapping_status,mapping_note
```

### 4.1 行

列と**タイプ=A**ターゲットカラムを生成します。

重要な分野:

- **フィールド名**出力列の順序を制御して下さい。
- **フィールド名**放射対象カラム名です。
- **semantic_path**UADC Structured CSV 値を識別します。
- **参考文献**対象の定義文書から来ます。
- **マッピング status**お問い合わせ**ダイレクト**, **お見積り**, **必須 transformation**または**お知らせ**.
- **マッピングノート**意味のある近似やデータのギャップを説明します。

コンバーターはStructured CSVの最終セグメントのソース列を導きます**semantic_path**.

例:

```
$.invoice.invoiceNumber -> InvoiceNumber
$.invoice.seller.sellerIdentifier -> SellerIdentifier
```

### 4.2 C行

列と**タイプ=C**row-適用範囲 の解像度に用いられる UADC のセマンティッククラスを定義します。

重要な分野:

- **フィールド名**semanticクラス名です。
- **参考文献**Structured CSVモデル定義からコピーされます。
- **semantic_path**semantic クラスを識別します。
- **multiplicity**クラスが繰り返すことができるかどうかを決定します。

反復クラス は multiplicity の上限が**\***, **ログイン**, **ログイン**1よりも大きい

コンバーターはクラス意味パスからStructured CSV ディメンション列を導きます。

例:

```
$.invoice.invoiceLine -> dInvoiceLine
```

## 5. 繰り返し 行スコープ

コンバータは、最も深い繰り返しからターゲット行スコープを決定します**ツイート**非インデックスで使用した祖先**ツイート**行。

インボイス レベル ターゲットは 行スコープ を繰り返さない。 コンバーターは、スパース Structured CSV 行を インボイス ごとに 1 つのターゲット行にマージします。

ラインレベルのターゲットの使用**$.invoice.invoiceLine**として 行スコープ. コンバーターはそれぞれ1つのターゲット行を出力します**dInvoiceLine**各行列に親インボイス値が出現してマージします。

その他の反復クラスは、VATの故障や手当などの意味バインディングテーブルがインデックスされていないリピート先祖としてこれらのクラスを使用するときに同じルールに従ってください。

## 6. インデックス化された繰り返し値

繰り返されたグループが水平にターゲット 列に拡大しなければならないとき、ゼロ ベースのインデックス 意味パス を使用します。

例:

```
$.invoice.vatBreakdown[0].vatCategoryCode
$.invoice.vatBreakdown[1].vatCategoryCode
$.invoice.vatBreakdown[2].vatCategoryCode
```

インデックスされたパスは追加の出力行を作成しません。 現在のインボイスまたは現在の繰り返し行のコンテキスト内で指定された発生を選択します。

ISO 21378ヘッダーバインディングは、インデックス付きVATブロードダウンパスを使用します。**税1**コース**税4**. インボイス ノートと支払いの指示は、ADC ヘッダーのフィールドが単数であるため、発生ゼロも使用されます。 細部の結合は繰り返されたを使用します**インボイスライン**出力行スコープのクラス。EN 16931はインボイスラインごとの1つのVATの分類を許可します、従って**税1 タイプ コード**詳細な行を直接マップすることができます。

## 7. 内部データ構造

**read csv rows(パス)**リターン:

```
list[dict[str, str]]
```

各辞書は、ヘッダ名でキーする1つのCSV行です。

**セマンティッククラス**ストア:

- **semantic_path**;
- **multiplicity**.

繰り返し**セマンティッククラス**行は以下のように収集されます。

```
dict[str, SemanticClass]
```

**セマンティックビンディング**1つのターゲットコラムの結合を貯えて下さい:

- **パスワード**;
- **ターゲット コラム**;
- **semantic_path**;
- **正規化 semantic_path**;
- **ソース 列**;
- **リピート グループ パス**;
- **リピート group column**;
- **リピート インデックス**;
- **デフォルト値**;
- **お問い合わせ**.

**load bindings(binding csv) は、**リターン:

```
list[SemanticBinding]
```

リストはソートされます**フィールド名**または**パスワード**それからターゲット カラムの名前によって。

## 8. 処理機能

**load bindings(binding csv) は、**バインディング表 のレコードを繰り返し読みます**ツイート**クラスの作成**セマンティックビンディング**オブジェクト**ツイート**行、 意味パスs からソース列を導き、 バインディング表 から 行スコープ を繰り返して解決します。

**row 適用範囲 group(バインド)**対象ビュー で使用される最も深い繰り返しグループを選択します。 これは、出力がインボイスレベルまたは繰り返しレベルであるかを決定します。

**transform rows(rows、バインディング)**バインディング表 を Structured CSV 行に適用します。 行スコープ が繰り返されていない場合は、疎な行 を インボイス レベルの対象行にマージします。

**変換 repeated group rows(rows,binding, 適用範囲 path, 適用範囲 column)**繰り返しグループ発生ごとに1つのターゲット行を生成します。**dInvoiceLine**.

**row repeat indices(source row、バインディング、repe counts)**インデックスされた繰り返しパスのゼロベースの発生番号を割り当てます。

**merge values(target row、source row、バインディング、repeat indices)**non-empty Structured CSV 値を対象カラムにコピーします。 各対象カラムの非空でない値を使用します。

**output path(input csv、 output dir、拡張子、 output filename、binding csv)**出力を下書きします:

```
out/phase2/<target-family>/<structured-csv-stem>/<target-view>.<extension>
```

お問い合わせ**--output-filename**1つの入力ファイルに対して供給されます。

## 9. 出力契約

出力ヘッダーは順序に続きます**ツイート**意味バインディング CSV の行。

デフォルト出力プリセット:

|フォーマット | デリミター | エクステンション |
| --- | --- | --- |
| **ログイン** | **|** | **.psvの** |
| **ログイン** | **,** | **ログイン** |

対象ビュー ステムは結合ファイル名から派生します。 例えば:

```
ADS_Invoices_Received_PSV_Binding.csv -> Invoices_Received.psv
ADS_Customer_Master_PSV_Binding.csv -> Customer_Master.psv
ISO21378_PUR_Invoice_Received_CSV_Binding.csv -> PUR_Invoice_Received.csv
```

## 10. 非目標

- コンバーターはXMLを解析しません。
- コンバーターはXPathを使用しません。
- コンバーターは、ターゲット列名だけからマッピングを推論しません。
- コンバータは、実行時に外部 LHM CSV を読みません。
- コンバーターはxBRL-CSVメタデータJSONを生成しません。
- コンバーターは会計カレンダーなしで会計年度または会計期間を導きません。
- コンバーターはライン総量またはライン税額を計算しません。
- コンバーターはERP 監査証跡、アカウント、ステータス、またはEN 16931から欠損している追加のビジネスセグメントの値を発明しません。

## 11. 運用ワークフロー

Phase 2 Phase 1 Structured CSV と対象のセマンティック バインディング表 を読み込みます。 必要な 対象ビュー のバインディングを選択し、対応するコンバーターを実行し、生成されたファイルを下で検査します。**out/phase2/**. すべてのマッピングは、**フィールド名**, **semantic_path**, クラス**multiplicity**、および結合順序。

バインディング**タイプ=C**行はクラス適用範囲sを確立します。**タイプ=A**rows はターゲットフィールドを定義します。 コンバータは、最終セマンティックパスセグメントからStructured CSVのソース列を導き、各フィールドを最も深い反復クラス祖先に割り当てます。

## 12. ADS PSV

ADS PSV 出力は、**src/semantic_binding.py**お問い合わせ**ログイン**プリセット 6つのADSの結合ビューカバーインボイスと概念の証明によって要求されるマスターデータ視点。 各出力ヘッダはバインディングオーダーに従い、繰り返し対象レコードはバインディングで選択した繰り返しのセマンティッククラスに従います。

ERP ユーザー履歴、投稿状況、ジャーナルアカウント、または期間クローズ処理に依存するフィールドは、EN 16931 がソース値を供給しないままです。 これは宣言されたソース・データ境界で、推論されたゼロまたはデフォルトではありません。

## 13. ADS XBRL GL

ADS XBRL GL インスタンスが生成されます。**src/syntax_binding_ads_xbrl_gl.py**. 同じ意味パスsおよびクラス適用範囲sはADS PSV6つを送りますXBRL GLs。 ジェネレータは、選択したバインディングに応じて、コンテキスト、ユニット、ドキュメント情報、selector、およびターゲットファクトを作成します。

売り手 ID は、識別子参照 selector を使用します。**識別子Type=V**. 売り手 郵便住所の事実は一致の下の属します**識別子 郵便番号**コンテナ。 結合テーブルの結合生成とXBRL構造は、このselectorの祖先を保存しなければなりません。そうしないで売り手リストはPhase 1が含まれている場合でも、そのアドレスを省略するように表示されます。

## 14. ISO 21378 ADC

ISO 21378 ADC 実装は 4 つの インボイス semantic-バインディング表s と CSV プリセットを使用します。**src/semantic_binding.py**. 同じStructured CSVが独立した設計会計データ インターフェイスに与えることができることを示します。

インボイス がサポートするフィールドに限られます。 トランザクション承認、ユーザーアクション履歴、投稿詳細、クローズ情報、およびレポート生成状態はERPソースが必要です。 生成された ADC ファイルは、 既知の インボイス 値 と 明示的なギャップを 考慮証拠を発明せずに保存します。

## 15. 機能レベルの処理の参照

### 15.1 ADSとADCの変換

- **load bindings ディレクティブ**クラスと属性の行をシーケンスで読み、検証します。
必須対象分野
- **インデックス  semantic_path**明示的にインデックスされた繰り返し値を認識します。
- **source column for path の一覧**最後のセマンティックパスセグメントをマップ
Structured CSV 列。
- **ディメンション コロン for path**関連する ディメンション を識別する
クラスパス。
- **イマラチオ class ancestor**そして、**resolve bindings for classes ディレクティブ**パスワード
各ターゲットフィールドを有効繰り返し 行スコープ にします。
- **変換 rows**現在の祖先値を維持し、ターゲット行を作成します。
- **変換 repeated group rows**独自にインデックスを繰り返す
レコード。
- **マージ 値**コピーは、現在の行が所有する値のみであり、要求される値のみ
ターゲット結合。
- **write target file ディレクティブ**注文したPSVまたはCSVヘッダーとレコードを書きます。

単数子クラス は、現在の繰り返しの祖先にマージされます。 繰り返された子供は最初の発生から独立したターゲットレコードを作成し、Structured CSV契約を一致させます**DATA_MODEL.md**.

### 15.2 ADS XBRL GL 生成

- **load bindings ディレクティブ**ADS XBRL GL の結合行を読み、正規化します。
- **validate hierarchical row 適用範囲s は、**同じを強制する parent/repeated-child
Phase 1 として分離。
- **rows for binding ディレクティブ**各セマンティックファクトのソース行を選択します。
- **ユニット ref from rule**そして、**decimals for item ディレクティブ**導体XBRLユニットと小数
精度。
- **path parts(パス)**, **parse path step ディレクティブ**と**selector マッチ**通訳対象
XBRL GL パスと selector 述語。
- **コンテナ for path**そして、**確認する 子供**選択したターゲットを正確に作成する
識別子参照アドレスコンテナを含む階層。
- **append item ディレクティブ**空の数値値を抑制しながら事実を作成します。
- **ビルドインスタンス**コンテキスト、単位、文書情報、およびバインドを作成する
1つの対象ビューの事実。
- **リオーダーツリー**安定したターゲット順序で子供をシリアライズします。

## 16. 検証とトラブルシューティング

すべての Phase 1 の例のすべてのターゲットファイルを検証します。, 唯一の 1 つの代表者 インボイス. ADS XBRL GL の場合、Arelle バリデーションを実行し、すべてのインスタンスがスキーマと関係をロードしていることを確認します。 ADS PSV および ADC の場合、ヘッダの注文、レコードのカウント、区切り文字、および代表的な繰り返された値を確認します。

フィールドが不在の場合、この順序でチェックしてください。

1. Phase 1 Structured CSV に存在する値。
2. 意味パス は、予想されるソース列で終了します。
3. すべて**タイプ=C**祖先と多重性は結合に存在します。
4. selector コンテキストは 結合表 で保持されます。
5. ターゲット・パスとターゲット・フィールド名がポップアップ表示されます。
6. 行は 対象ビュー で期待される繰り返し 適用範囲 に属します。


## 17. 意味バインディング 変換の概要

### 意味バインディング 変換 文書

このディレクトリは、構造化されたCSV-to-target-flat-file変換プログラムを文書化します。

意味バインディング コンバーターは Phase 1 UADC Structured CSV および 意味バインディング CSV を読みます。 ADS PSV や ISO 21378 ADC CSV などの Phase 2 ターゲットフラットファイルを書きます。 バインディング表 は、対象カラムが UADC を受け取るかを定義します。**semantic_path**値、およびどのセマンティッククラスが繰り返されたターゲット行を制御します。

ISO 21378:2019 ADC インボイス は、現在表38、39、53、54をカバーしています。 対象のTAXグループが4つの数値列セットに展開され、ビジネスSEGMENTは5つの数列に展開され、各々がCSVヘッダが一意であるようにします。 各ターゲット行もレコードを記録**マッピング status**そして、**マッピングノート**. これらの列は、セマンティックな近似、必要な変換、および EN 16931 インボイス から利用できないソースデータから直接マッピングを区別します。

これら4つのビューは、計画されたPhase 2PoCベースラインのISO 21378部分を完了します。 補完とは、ターゲット定義、バインディング、CSV生成、回帰実行、および明示的なギャップ分類が存在することを意味します。 EN 16931 ソース インボイス から完全な ISO 21378 データ完全性を主張しません。

内部を含むブロッカー処理モデルと共有される実装レベルの詳細**dict/list/dataclass**オブジェクトと関数レベルのデータフロー、使用**DATA_MODEL.md**, 第15章.

#### ファイル

- **program_specification.md**- コンバータ入力、出力、意味バインディング行、繰り返し 行スコープ、インデックス化された繰り返し値、出力ネーミング、および非目標を定義します。
- **user_guide.md**- ADS PSV と CSV 生成、ディレクトリ入力、トラブルシューティングのコマンド例を指定します。
- **iso21378_adc_invoice_coverage.md**- レコード ISO 21378 ADC インボイス マッピングカバレッジ、データギャップ、 Phase 1 回帰結果。

#### 関連ディレクトリ

- **../../src/**- コンバーターの実装、特に**semantic_binding.py**.
- **../../specs/bindings/semantic/**- アクティブ 意味バインディング CSV ファイル。
- **../../specs/bindings/syntax/**- 構文バインディング Phase 1 Structured CSV のモデルを定義する CSV ファイル。
- **../../out/phase1/**- Phase 1 Structured CSV 入力。
- **../../out/phase2/**- 生成されたPhase 2ターゲット出力。

Phase 2 意味バインディング は共通 Structured CSV から始まります。 直接XMLを解析せず、ソースXMLXPathの式に依存しません。



## 18. 意味バインディング 利用者ガイド

### 利用者ガイド: 意味バインディング 構造化されたCSV-to-Flat-File変換

#### 1. 働くディレクトリ

コマンドを実行する**UADC ポック**ディレクトリ:

```
cd UADC_PoC
```

Windows PowerShell 用の Python コマンドを設定します。

```
$python = 'python'
```

macOS または Linux のシェルの場合:

```
PYTHON=python3
```

#### 2. 主なスクリプト

使用:

```
src/semantic_binding.py
```

スクリプトは Phase 1 Structured CSV を Phase 2 ターゲット PSV または CSV ファイルを 意味バインディング CSV に変換します。

#### 3。 ADSを生成します。 インボイス 受信PSV

実行:

```
& $python .\src\semantic_binding.py `
  .\out\phase1\openpeppol_ubl_invoice_minimal.csv `
  -b .\specs\bindings\semantic\ADS_Invoices_Received_PSV_Binding.csv `
  -o .\out\phase2\ADS_PSV `
  --format psv
```

出力:

```
out/phase2/ADS_PSV/openpeppol_ubl_invoice_minimal/Invoices_Received.psv
```

#### 4. ADS インボイス 受信ライン PSV を生成

実行:

```
& $python .\src\semantic_binding.py `
  .\out\phase1\openpeppol_ubl_invoice_minimal.csv `
  -b .\specs\bindings\semantic\ADS_Invoices_Received_Lines_PSV_Binding.csv `
  -o .\out\phase2\ADS_PSV `
  --format psv
```

出力:

```
out/phase2/ADS_PSV/openpeppol_ubl_invoice_minimal/Invoices_Received_Lines.psv
```

このターゲットは、繰り返し 行スコープ を持っています。 バインディング表 には**タイプ=C**お問い合わせ**$.invoice.invoiceLine**繰り返して multiplicity で、コンバータは 1 行/**dInvoiceLine**出現。

#### 5. すべて Phase 1 Structured CSV を変換します。 ファイル

実行:

```
& $python .\src\semantic_binding.py `
  .\out\phase1 `
  -b .\specs\bindings\semantic\ADS_Invoices_Received_PSV_Binding.csv `
  -o .\out\phase2\ADS_PSV `
  --format psv
```

各入力 CSV は、入力 Structured CSV ステム で指定された 1 つの出力ディレクトリを作成します。

例:

```
out/phase2/ADS_PSV/Allowance-example/Invoices_Received.psv
```

#### 6. PSVの代わりにCSVを生成

使用条件**--format csv**:

```
& $python .\src\semantic_binding.py `
  .\out\phase1\openpeppol_ubl_invoice_minimal.csv `
  -b .\specs\bindings\semantic\ADS_Invoices_Received_PSV_Binding.csv `
  -o .\out\phase2\ADS_CSV `
  --format csv
```

出力:

```
out/phase2/ADS_CSV/openpeppol_ubl_invoice_minimal/Invoices_Received.csv
```

#### 7. 生成 ISO 21378 ADC インボイス CSV

ISO 21378:2019 表 53 のための購入 インボイス ヘッダーの結合を使用して下さい:

```
& $python .\src\semantic_binding.py `
  .\out\phase1\bis-billing3-examples\Allowance-example.csv `
  -b .\specs\bindings\semantic\ISO21378_PUR_Invoice_Received_CSV_Binding.csv `
  -o .\out\phase2\ISO21378_ADC `
  --format csv
```

出力:

```
out/phase2/ISO21378_ADC/Allowance-example/PUR_Invoice_Received.csv
```

使用条件**ISO21378_PUR_Invoice_Received_Details_CSV_Binding.csv**テーブル54用 対応する使用**サール**テーブル38と39用のファイル。

レビュー**マッピング status**出力を完全なADCの提出として扱う前に各結合:

- **ダイレクト**UADC 値がコピーできることを意味します。
- **お見積り**つまり、最も近い EN 16931 値がコピーされますが、意味は同一ではありません。
- **必須 transformation**計算、ルールの解析、コード変換、または会計カレンダーが必要です。
- **お知らせ**EN 16931 インボイス は、必要な ERP または 監査 datum が含まれていません。

#### 8. コマンドオプション

基本フォーム:

```
& $python .\src\semantic_binding.py INPUT `
  -b BINDING_CSV `
  -o OUTPUT_DIR `
  --format psv
```

オプション:

- **インプット**: 1 Structured CSV ファイルまたは Structured CSV ファイルを含むディレクトリ。
- **-bの**, **--binding-csv**: 意味バインディング CSV.
- **ツイート**, **--output-dir**: 出力ディレクトリ
- **--format**: 出力プリセット、いずれか**ログイン**または**ログイン**.
- **--delimiter**: 明示的な区切り文字。 このオーバーライド**--format**.
- **--extension**: 明示的な出力延長。 このオーバーライド**--format**.
- **--output-filename**: 単一ファイル入力の出力ファイル名を明示的に出力します。

#### 9. バインディング表 レビューポイント

対象分野:

- 使用条件**タイプ=A**.
- 放射対象カラム名を入力**フィールド名**.
- UADC ソースを入れる**semantic_path**.
- お問い合わせ**フィールド名**ターゲット出力順序で。

row-適用範囲 クラスの場合:

- 使用条件**タイプ=C**.
- セマンティッククラスのパスを**semantic_path**.
- Structured CSV モデルの記述をで置いて下さい**参考文献**.
- multiplicity をクラスに入れる**multiplicity**.

水平に繰り返される値のため:

- たとえばゼロベースのインデックスパスを使用する**$.invoice.vatBreakdown[0].vatCategoryCode**.
- 反復クラスをaとして含んで下さい**タイプ=C**同じバインディング表の行。

#### 10. トラブルシューティング

出力カラムが空白の場合、その列が空白になっていることを確認してください。**semantic_path**最終セグメントは、UpperCamelCase 変換後の Structured CSV ソース列にマッチします。

行レベルのファイルが 1 行しかない場合、 バインディング表 に繰り返されることを確認してください。**タイプ=C**行**$.invoice.invoiceLine**と multiplicity**1..*** または**0..***.

対象となるファイル名が予期せぬ場合は、結合CSVファイル名を確認してください。 コンバーターは、などの名前から対象ビューを導きます**ADS_Invoices_Received_PSV_Binding.csv**.



## 19. ISO 21378 ADC インボイス カバー

### ISO 21378 ADC インボイス 意味バインディング カバー

#### 適用範囲

Phase 2 意味バインディング は、ISO 21378:2019 監査データ収集 インボイス のビューをカバーしています。

|ADCテーブル | 対象ビュー | 結合ファイル |
| --- | --- | --- |
|テーブル 38 | SALインボイス ジェネレーション |**ISO21378_SAL_Invoice_Generated_CSV_Binding.csv** |
|表39 | SAL インボイス 生成詳細 |**ISO21378_SAL_Invoice_Generated_Details_CSV_Binding.csv** |
|表53 | PUR インボイス 受付中**ISO21378_PUR_Invoice_Received_CSV_Binding.csv** |
|テーブル 54 | PUR インボイス 新着情報 |**ISO21378_PUR_Invoice_Received_Details_CSV_Binding.csv** |

結合はISO 21378フラットインボイスモデルを使用します。 繰り返したTAXグループが4つの数値列セットに展開されます。 業務委託は5つの数列に拡大します。

この適用範囲はPoCのPhase 2に完全です。 補完基準は、すべての現在のPhase 1入力に対して生成されたCSV出力と、直接コピーできないフィールドの明示的な分類をレビュー対象の定義、実行可能結合、生成されたCSV出力です。 すべてのISO 21378フィールドのフル人口は、 EN 16931ソースモデルがERPの監査とデータの投稿が含まれていないので、完全な基準ではありません。

#### マッピングカバレッジ

|対象ビュー | フィールド | ダイレクト | 近似 | 変換条件 | 利用不可 | バウンドパス |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|PUR インボイス 受取人 | 42 | 17 | 5 | 5 | 5 | 5 | 15 | 15 | 22 |
|PUR インボイス 受入詳細 | 39 | 12 | 1 | 2 | 24 | 13 |
|SAL インボイス 生成 | 41 | 17 | 4 | 5 | 15 | 21 |
|SALインボイス 生成詳細 | 39 | 11 | 1 | 2 | 25 | 12 |

**バウンドパス**直接マッピングと近似マッピングの合計です。 現在の意味バインディングコンバーターは値をコピーし、それらを計算または解析しないため、必要な変換は境界としてカウントされません。

#### データの効率性評価

Phase 1 EN 16931 Structured CSV は、有用な インボイス コアプロジェクションに十分です。 インボイス 識別子、日付、パーティー、通貨、合計、支払い情報、VAT の故障、 インボイス 行、数量、価格、アイテム識別子、購入または販売注文参照を提供します。

完全ISO 21378 ADC配送には十分ではありません。 主なギャップは次のとおりです。

- 会計カレンダーが必要な会計年度・経理期間
- パーシングまたは専用のソースフィールドを必要とする正規化された支払い期間コンポーネント。
- ERP 作成、承認、最終変更されたイベントのアクティビティレコード。
- インボイス ライフサイクル状態;
- 一般的なレガーデビット、クレジット、および税務投稿アカウント。
- 計算または配分を必要とする総行の量およびライン税額;
- 基本的な単位の量およびコードを分けて下さい;
- 単一のEN 16931の経理基準を超えた複数の事業セグメント値。
- EN 16931 は 1 つの インボイス ライン上の複数の税構造で、1 行につき 1 つの VAT 分類を定義します。

そのため、現在のバインディングはPhase 2の証拠の生成とマッピングギャップ解析に適していますが、フルISO 21378 ADCの完全性を主張していません。

#### 試験結果

全10個の電流Phase 1Structured CSVインボイスファイルに4つのバインディングを適用しました。 生成された40個のターゲットファイルを実行します。

|対象ビュー | ファイル | 合計データ行 | ファイルごとの最小行 | ファイルごとの最大行 |
| --- | ---: | ---: | ---: | ---: |
|PUR インボイス 受取人 | 10 | 10 | 1 | 1 | 1 | 1 | 1
|PUR インボイス 受入詳細 | 10 | 18 | 1 | 3 | 3 |
|SAL インボイス 生成済み | 10 | 10 | 1 | 1 | 1 | 1
|SALインボイス 生成詳細 | 10 | 18 | 1 | 3 |

4つのバインディングの非空 意味パス もチェックされていました**EN16931_CIUS_Invoice_LHM.csv**. 現在の UADC LHM にあるすべての境界線のパスが存在します。
