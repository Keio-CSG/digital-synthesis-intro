# デジタル論理合成入門 — RTL から signoff まで

小さな回路 (4レーン MAC) で、RTL シミュレーション → 論理合成 → 等価性検証 → 配置配線 (CTS 込み) → 寄生抽出 → signoff STA → ゲートレベルシミュレーション → DRC/LVS を一周する教材リポジトリです。

- 解説サイト: `docs/` (GitHub Pages)。`python3 tools/build_site.py` で再生成。
- 結果の画像（配置・クロックツリー・電源・GDS）: `python3 tools/render_layout.py`（要 matplotlib）
- 実行: `make all`（各ステップは `make syn` のように単体でも実行可）。

## 使い方
1. `config/*.example.*` を `config/` 内でコピーし（`.example` を外す）、自分の環境の値で埋める。
   実体は `.gitignore` により **コミットされません**（ライブラリ・ルールデック・ツールの場所などを含むため）。
2. `make all`

詳細は解説サイトの「01 セットアップ」を参照。

## 構成
`rtl/` RTL ・ `tb/` テストベンチ ・ `const/` SDC ・ `sim/` ・ `dc/` ・ `fm/` ・ `icc2/` ・ `rcx/` ・ `sta/` ・ `verif/` ・ `config/` 環境依存 ・ `docs/` サイト

## ライセンス・注意
MIT License（`LICENSE`）。プロセス固有のデータ（ライブラリ・ルールデック等）は含まれていません。各自、権利を持つものを使用してください。
