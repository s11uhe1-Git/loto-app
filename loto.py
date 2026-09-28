"""CSV validation and candidate generation; no network or file persistence."""
import csv
import io
import random
import re
from collections import Counter

GAMES = {"ロト6": (6, 43), "ロト7": (7, 37)}
METHODS = ["全期間の頻度", "直近の頻度", "低頻度の数字", "奇偶バランス", "ランダム"]


def read_csv(data):
    if len(data) > 5 * 1024 * 1024:
        raise ValueError("CSVは5MB以下にしてください。")
    for encoding in ("utf-8-sig", "cp932"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("文字コードをUTF-8またはCP932（Shift_JIS）で保存してください。")
    try:
        records = list(csv.reader(io.StringIO(text), strict=True))
    except csv.Error as exc:
        raise ValueError("CSVの引用符や区切りを確認してください。") from exc
    if not records:
        raise ValueError("CSVが空です。")
    headers = [h.strip() for h in records[0]]
    if not all(headers) or len(set(headers)) != len(headers):
        raise ValueError("1行目に、空欄や重複のない列名を指定してください。")
    rows = []
    for line, row in enumerate(records[1:], 2):
        if not row or not any(v.strip() for v in row):
            continue
        if len(row) != len(headers):
            raise ValueError(f"レコード{line}の列数がヘッダーと一致しません。")
        rows.append((line, dict(zip(headers, row))))
    if not rows:
        raise ValueError("当選番号のデータ行がありません。")
    return headers, rows


def suggest_columns(headers, count):
    # Exported sheets may suffix repeated 本数字 headers with .1, .2, ...
    dotted = ["本数字"] + [f"本数字.{i}" for i in range(1, count)]
    if all(name in headers for name in dotted) and f"本数字.{count}" not in headers:
        return dotted
    for pattern in ("第{}数字", "本数字{}", "数字{}", "n{}"):
        names = [pattern.format(i) for i in range(1, count + 1)]
        if all(name in headers for name in names):
            return names
    return []


def validate_draws(rows, columns, game):
    count, maximum = GAMES[game]
    if len(columns) != count or len(set(columns)) != count:
        raise ValueError(f"本数字の列を{count}列選択してください。")
    draws = []
    for line, row in rows:
        values = [row[c].strip() for c in columns]
        if not all(re.fullmatch(r"[0-9０-９]+", v) for v in values):
            raise ValueError(f"レコード{line}：本数字に空欄や整数以外の値があります。")
        numbers = tuple(sorted(int(v) for v in values))
        if any(n < 1 or n > maximum for n in numbers):
            raise ValueError(f"レコード{line}：本数字は1〜{maximum}で指定してください。")
        if len(set(numbers)) != count:
            raise ValueError(f"レコード{line}：同じ抽選内に重複した本数字があります。")
        draws.append(numbers)
    if not draws:
        raise ValueError("当選番号のデータがありません。")
    return draws


def frequencies(draws, maximum):
    counts = Counter(n for draw in draws for n in draw)
    return [counts[n] for n in range(1, maximum + 1)]


def weighted_sample(rng, pool, weights, count):
    pool, weights = list(pool), list(weights)
    result = []
    for _ in range(count):
        index = rng.choices(range(len(pool)), weights=weights, k=1)[0]
        result.append(pool.pop(index))
        weights.pop(index)
    return result


def generate(draws, game, recent=30, seed=None):
    """Draws must be validated and ordered oldest to newest."""
    if not draws or recent < 1:
        raise ValueError("有効な抽選履歴と直近回数が必要です。")
    count, maximum = GAMES[game]
    rng = random.Random(seed)
    pool = list(range(1, maximum + 1))
    full = frequencies(draws, maximum)
    short = frequencies(draws[-recent:], maximum)
    weights = [[x + 1 for x in full], [x + 1 for x in short],
               [1 / (x + 1) for x in full], [1] * maximum, [1] * maximum]
    results, seen = [], set()
    for method, weight in zip(METHODS, weights):
        for _ in range(1000):
            if method == "奇偶バランス":
                odd_count = count // 2 + (rng.randrange(2) if count % 2 else 0)
                numbers = rng.sample(pool[::2], odd_count) + rng.sample(pool[1::2], count - odd_count)
            else:
                numbers = weighted_sample(rng, pool, weight, count)
            numbers = tuple(sorted(numbers))
            if numbers not in seen:
                seen.add(numbers)
                results.append((method, numbers))
                break
        else:
            raise ValueError("異なる5パターンを生成できませんでした。再試行してください。")
    return results


def export_csv(results, game):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["種類", "方式"] + [f"本数字{i}" for i in range(1, GAMES[game][0] + 1)])
    for method, numbers in results:
        writer.writerow([game, method, *numbers])
    return buffer.getvalue().encode("utf-8-sig")


def sample_csv(game):
    rng = random.Random(2026)
    count, maximum = GAMES[game]
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["回号"] + [f"本数字{i}" for i in range(1, count + 1)])
    for index in range(1, 61):
        writer.writerow([index, *sorted(rng.sample(range(1, maximum + 1), count))])
    return buffer.getvalue().encode("utf-8-sig")
