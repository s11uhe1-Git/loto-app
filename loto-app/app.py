import hashlib
import math
import streamlit as st
from loto import GAMES, export_csv, frequencies, generate, read_csv, sample_csv, suggest_columns, validate_draws

st.set_page_config(page_title="LOTO LAB | ロト候補番号", page_icon="🎱", layout="centered")
st.markdown("<style>.block-container{max-width:960px;padding-top:2.5rem}"
            ".balls{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 20px}"
            ".ball{display:inline-flex;width:46px;height:46px;align-items:center;"
            "justify-content:center;border-radius:50%;background:#0f766e;color:white;"
            "font-size:20px;font-weight:700}</style>", unsafe_allow_html=True)
st.caption("LOTO LAB / 過去のデータから、番号選びを楽しむ")
st.title("ロトの候補番号を、5パターン。")
st.write("当選履歴のCSVを読み込み、5つの選び方で次回の候補を試算します。")
st.info("公正で独立した抽選では、過去の出現傾向によって次回の当選確率は上がりません。表示する番号は試算候補であり、当選を保証する予測ではありません。")

game = st.radio("くじの種類", list(GAMES), horizontal=True)
count, maximum = GAMES[game]
st.caption(f"1〜{maximum}から異なる{count}個を選びます。本数字のみを分析し、ボーナス数字は含めません。")
st.subheader("1. 当選履歴を読み込む")
demo = st.checkbox("架空のサンプルデータで試す")
st.download_button("CSVの見本をダウンロード（架空データ）", sample_csv(game),
                   file_name=f"sample_loto{count}.csv", mime="text/csv")
uploaded = st.file_uploader("当選履歴CSV（UTF-8 / CP932、5MBまで）", type=["csv"], disabled=demo)
st.caption("ヘッダー付き・カンマ区切り。1行に1回分を記載し、ロト6とロト7は別ファイルにしてください。")
if not demo and uploaded is None:
    st.stop()
data = sample_csv(game) if demo else uploaded.getvalue()
if demo:
    st.warning("現在は動作確認用の架空データを使っています。実際の当選履歴ではありません。")
try:
    headers, rows = read_csv(data)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

with st.expander("読み込んだCSVを確認", expanded=True):
    st.dataframe([row for _, row in rows[:10]], width="stretch")
    st.caption(f"全{len(rows):,}行のうち、先頭10行までを表示")
identity = hashlib.sha256(data + game.encode()).hexdigest()
columns = st.multiselect(f"本数字の列を{count}列選択（ボーナス数字は除外）", headers,
                         default=suggest_columns(headers, count), key=f"columns-{identity}")
order = st.radio("CSVの行の並び順", ["古い回 → 新しい回", "新しい回 → 古い回"], horizontal=True)
st.caption("日時や回号による自動並べ替えは行いません。CSVを時系列に並べてから指定してください。同じ回を重複登録しないでください。")
try:
    draws = validate_draws(rows, columns, game)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
if order == "新しい回 → 古い回":
    draws.reverse()

st.subheader("2. 試算する")
recent = st.number_input("直近の頻度に使う抽選回数", min_value=1, max_value=len(draws),
                         value=min(30, len(draws)), step=1, key=f"recent-{identity}")
left, right = st.columns(2)
left.metric("分析する抽選履歴", f"{len(draws):,} 回")
right.metric("1口の1等確率（公正な抽選）", f"1 / {math.comb(maximum, count):,}")
if len(draws) < 30:
    st.caption("履歴が30回未満のため、出現頻度は特に偏りやすくなります。")
signature = (identity, tuple(columns), order, recent)
if st.session_state.get("signature") != signature:
    st.session_state.pop("results", None)
    st.session_state["signature"] = signature
if st.button("候補番号を5パターン生成", type="primary", width="stretch"):
    st.session_state.results = generate(draws, game, recent)

if "results" in st.session_state:
    st.subheader("今回の候補番号")
    for index, (method, numbers) in enumerate(st.session_state.results, 1):
        st.write(f"**{index:02d} / {method}**")
        st.markdown('<div class="balls">' + ''.join(f'<span class="ball">{n:02d}</span>' for n in numbers) + '</div>', unsafe_allow_html=True)
    st.download_button("5パターンをCSVで保存", export_csv(st.session_state.results, game),
                       file_name=f"loto{count}_candidates.csv", mime="text/csv")
    st.caption("生成ボタンをもう一度押すと再抽選します。5組は互いに異なりますが、組をまたぐ数字の重複はあります。")

with st.expander("過去の出現回数を見る"):
    counts = frequencies(draws, maximum)
    st.bar_chart({"数字": list(range(1, maximum + 1)), "出現回数": counts}, x="数字", y="出現回数")
    st.dataframe([{"数字": n, "出現回数": counts[n - 1], "出現率（抽選回あたり）": f"{counts[n - 1] / len(draws):.1%}"} for n in range(1, maximum + 1)], width="stretch")
with st.expander("試算方法について"):
    st.markdown("""
1. **全期間の頻度**：出現回数＋1を重みにして抽出します。
2. **直近の頻度**：指定した直近回数の出現回数＋1を重みにします。
3. **低頻度の数字**：1 ÷（出現回数＋1）を重みにします。未出現数字が次回に出やすくなることを意味しません。
4. **奇偶バランス**：ロト6は奇数3・偶数3、ロト7は奇数3・偶数4または奇数4・偶数3で抽出します。
5. **ランダム**：すべての数字に同じ重みを与えます。

各組の中では数字を重複させず、昇順で表示します。組が重複した場合は再抽出します。
これは過去データを使った候補生成であり、予測精度の向上を実証したモデルではありません。
CSVは処理のため実行サーバーへ送信されます。アプリはCSVをファイルやデータベースに保存しません。
""")
