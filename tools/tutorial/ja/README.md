# チュートリアルツールの実装

このディレクトリには、学習、プロトタイピング、バインディングテーブルの実験のための小型、自己完結型コンバータの実装が含まれています。

- **syntax_binding_sample.py**はXML-to-flat-CSV抽出物をXML-to-flat-CSVで示します
コンパクト構文バインディングと限られたXPath評価器。
- **semantic_binding_sample.py**は行列の投影を a から実証します
Structured CSV は、レガシーバインディング列の互換性のある CSV に。

これらのプログラムは、運用中の UADC コンバーターではありません。 生産 Phase 1 および Phase 2 処理用途:

```
src/syntax_binding.py
src/syntax_binding_ads_xbrl_gl.py
src/semantic_binding.py
```

別々の**src/tutorial/**ディレクトリには、操作上のコンバータを呼び出す初心者ワークフローラッパーが含まれています。 この**tools/tutorial/**ディレクトリには、単純化されたコンバーターの実装が含まれている。

詳細な動作、引数、関数、制限及び検証方法は、[**構造化CSV、LHM及び結合**](../../../docs/ja/02_STRUCTURED_CSV_LHM_BINDINGS.md)に記載しています。運用手順は、[**環境、テスト及びチュートリアル**](../../../docs/ja/01_ENVIRONMENT_TESTS_TUTORIAL.md)に記載しています。
