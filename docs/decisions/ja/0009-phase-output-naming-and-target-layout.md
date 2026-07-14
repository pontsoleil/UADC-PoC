# 決定: 段階指向の出力ネーミングおよび対象ビューを使用して下さい レイアウト

## コンテンツ

初期出力名とディレクトリの混合履歴テスト名、コンバーター名、プロジェクトフェーズ名。 どのファイルが Phase 1 に属するか、どのファイルが Phase 2 のターゲット出力であるかを説明するのは困難でした。

PoC処理フローはPhase 1の共通Structured CSVの生成をPhase 2ターゲットビュー生成と区別します。

## デコレーション

1. Phase 1 出力は**out/phase1/**. で書かれています。
2. Phase 1 出力ファイル名は、拡張子のみで入力XMLステムを使用する
変更しました。
3. Phase 1 メタデータ JSON は同じステムと短い**.json**拡張子を使用します。
なし**.csv.metadata.json**.
4. Phase 2 ADS XBRL GL 出力は**out/phase2/ADS_XBRL_GL/**. で書かれています。
5. Phase 2 ADS PSV 出力は**out/phase2/ADS_PSV/**. で書かれています。
6. Phase 2 ISO 21378 ADC CSV 出力は**out/phase2/ISO21378_ADC/**.
7. ディレクトリ入力の場合はPhase 2の出力をStructured CSVのステムでグループ化します。
8. 対象のファイル名は、図1対象ビューの名称に従います。
**Invoices_Received.xbrl**,**Invoices_Generated_Lines.xbrl**,**Supplier_Listing.psv**,**Customer_Master.psv**,**PUR_Invoice_Received.csv**.

## コンシーケンス

- **samples/input/openpeppol_ubl_invoice_minimal.xml**になります
**out/phase1/openpeppol_ubl_invoice_minimal.csv**と**out/phase1/openpeppol_ubl_invoice_minimal.json**。
- Phase 2 XBRL GL**Allowance-example.csv**の出力が
**out/phase2/ADS_XBRL_GL/Allowance-example/Invoices_Received_Lines.xbrl**.
- ADS PSV**out/phase2/ADS_PSV/**. で同じグループ化規則に従う
- ISO 21378 ADC CSV は、同じグループ化規則に従います。
**out/phase2/ISO21378_ADC/**.
- Phase 2 ソースStructured CSVと対象ビューで出力を比較できます。
- これらの名前とディレクトリを使用するテストスクリプトが期待されます。
