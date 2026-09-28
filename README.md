# LOTO LAB — ロト6・ロト7 候補番号アプリ

過去の当選履歴をCSVで読み込み、5つの方式で候補番号を生成する日本語Streamlitアプリです。公正で独立した抽選では、どの組も当選確率は同じです。本アプリは当選確率の向上を実証した予測モデルではありません。

## 機能

- ロト6（1〜43から6個）・ロト7（1〜37から7個）の切り替え
- UTF-8 / UTF-8 BOM / CP932 のCSV読み込み（5MBまで）
- 本数字の列を手動指定。空欄・範囲外・小数・抽選内の数字重複を検出
- 全期間頻度、直近頻度、低頻度、奇偶バランス、ランダムの5組を生成
- 頻度グラフと結果CSVダウンロード
- 架空サンプルですぐに試せるデモ

## GitHubとStreamlit Community Cloudで公開する

1. ZIPを展開し、GitHubで新しいリポジトリ（例：`loto-app`）を作成します。
2. リポジトリの **Add file → Upload files** から、このフォルダ内のファイルをアップロードし、コミットします。`app.py`、`loto.py`、`requirements.txt`、`README.md` をリポジトリ直下に置いてください。`tests` と `.streamlit` も同じ構成で配置します。
3. `.streamlit` は隠しフォルダです。Macでは Finder の Command + Shift + . で表示できます。GitHub画面の **Add file → Create new file** に `.streamlit/config.toml` と入力して、同梱ファイルの内容を貼り付けても構いません。
4. [Streamlit Community Cloud](https://share.streamlit.io/)にログインし、GitHubアカウントを連携します。
5. **Create app** からGitHub上のアプリを選び、Repositoryに作成したリポジトリ、Branchに `main`（実際のブランチ名）、Main file pathに `app.py` を指定します。
6. **Advanced settings** で Python **3.12** を選び、**Deploy** を押します。APIキーやSecretsは不要です。
7. 発行されたURLを開き、「架空のサンプルデータで試す」で動作を確認してから、実際の履歴CSVをアップロードします。

フォルダごとアップロードして `loto-app/app.py` の配置にした場合は、Main file pathも `loto-app/app.py` に合わせてください。基本はファイルをリポジトリ直下に置く構成です。

作成時点ではGitHubリポジトリ作成・クラウド公開は未実施です。ご自身のアカウントで上記設定が必要です。

## CSV形式

ヘッダー付き、カンマ区切り、1行に1回分。本数字はそれぞれ独立した列に入れてください。例は架空の数字です。

```csv
回号,本数字1,本数字2,本数字3,本数字4,本数字5,本数字6
1,3,8,15,22,31,42
2,1,12,18,25,33,40
```

ロト7は `本数字7` まで追加します。日付・回号・ボーナス数字などの余分な列があっても構いませんが、本数字の列だけを選択してください。`第1数字`〜、`本数字1`〜、`数字1`〜、`n1`〜は自動選択できます。

履歴は古い順または新しい順に並べ、アプリでその順序を指定します。日付による自動ソートや回号の重複排除はしません。別の抽選で本数字が全く同じになる可能性があるため、番号が同じ行も自動削除しません。同じ抽選の二重登録はアップロード前に除いてください。

## 試算方式

全期間と直近は「出現回数＋1」、低頻度は「1 /（出現回数＋1）」を抽出の重みにします。各組内は重複なしで抽出し、5組が重なったときは再抽出します。奇偶バランスはロト6が3対3、ロト7が3対4または4対3です。生成ボタンを押すたびに新しい試算になります。

過去の頻度や奇偶の条件は番号選びの方針であり、当選確率が上がる根拠ではありません。ボーナス数字の予測・当選金計算・予測精度の検証機能は含みません。

## ローカル起動

Python 3.12を推奨。ターミナルでこのフォルダへ移動して実行します。

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

テスト：`python -m unittest discover -s tests -v`

CSVは実行サーバーのメモリで処理します。アプリからファイル・DBへの永続保存や外部APIへの転送は行いません。アップロードした履歴をGitHubへ入れる必要もありません。

## 参照

- [Streamlit公式の公開手順](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Streamlit公式のファイル構成](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)
- [みずほ銀行：ロト6](https://www.mizuhobank.co.jp/takarakuji/products/loto6/index.html)
- [みずほ銀行：ロト7](https://www.mizuhobank.co.jp/takarakuji/products/loto7/index.html)
