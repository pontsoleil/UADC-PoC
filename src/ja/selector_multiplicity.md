[English](../selector_multiplicity.md) | **日本語**

# selector_multiplicity

## 目的

この semantic-layer 必須 library は selector variant を考慮した effective multiplicity を計算します。

## 規則

selector は1つの canonical occurrence の variant を区別します。Class を plural にするためだけに accepted HMD を手作業で書き換える根拠にはなりません。

## 実行と安全

command は repository root から実行します。実行前に input path、output path、上書き動作を確認し、実験では task-local 又は明示承認された output location を使用します。

## Test

materially changed な code 又は条件に関係する test だけを実行します。入力、code、設定、依存 version、成果物、validation scope が materially 同一なら accepted PASS 証跡を再利用します。
