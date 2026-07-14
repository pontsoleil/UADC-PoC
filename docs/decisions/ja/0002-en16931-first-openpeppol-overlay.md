# 決定: EN 16931 最初, OpenPeppol オーバーレイ秒

## コンテンツ

PoC は LHM/HMD-style のセマンティックモデルとバインディング主導のコンバージョンが EN 16931-1 インボイス のモデルを、プロファイル固有の動作を追加する前に表すことができることを確認します。

OpenPeppol BIS Billing は単なる構文サンプルではありません。 EN 16931 の CIUS/profile レイヤーで、追加の制約、デフォルト値、および構文固有の要件を定義できます。

## デコレーション

1. EN 16931-1 LHM のカバレッジとコンバージョンに焦点を当てた最初のチェックポイントを保持します。
2. UBL Invoice XML は、そのチェックポイントのテスト入力構文として使用します。
3. OpenPeppol BIS Billing を CIUS/profile を追加した後のオーバーレイとして扱う
制約とOpenPeppol固有のバインディングチェック。

## コンシーケンス

- **specs/lhm/EN16931_CIUS_Invoice_LHM.csv**はEN 16931-1 BG/BTに対して監査されます
識別子。
- **specs/bindings/syntax/EN16931_UBL_Invoice_Syntax_Binding.csv**は現在の
変換ベースライン。
- OpenPeppol 固有の制約を文書化し、個別にテストする必要があります。
EN 16931 ベースラインが安定した後。
