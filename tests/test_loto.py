import unittest
from loto import GAMES, export_csv, generate, read_csv, sample_csv, suggest_columns, validate_draws


class LotoTests(unittest.TestCase):
    def test_dotted_main_number_headers(self):
        for game, (count, _) in GAMES.items():
            columns = ["本数字"] + [f"本数字.{i}" for i in range(1, count)]
            header = ["回号", "抽せん日", *columns, "ボーナス数字"]
            data = (",".join(header) + "\n" + ",".join(
                ["第2089回", "2026-04-02", *map(str, range(1, count + 1)), "15"])).encode("utf-8")
            headers, rows = read_csv(data)
            selected = suggest_columns(headers, count)
            self.assertEqual(selected, columns)
            draws = validate_draws(rows, selected, game)
            self.assertEqual(draws, [tuple(range(1, count + 1))])
            self.assertEqual(len(generate(draws, game, seed=42)), 5)
            self.assertEqual(suggest_columns(headers, 7 if count == 6 else 6), [])

    def test_both_games_and_invariants(self):
        for game, (count, maximum) in GAMES.items():
            headers, rows = read_csv(sample_csv(game))
            draws = validate_draws(rows, suggest_columns(headers, count), game)
            for seed in range(100):
                results = generate(draws, game, seed=seed)
                self.assertEqual(len(set(numbers for _, numbers in results)), 5)
                for _, numbers in results:
                    self.assertEqual(len(set(numbers)), count)
                    self.assertEqual(tuple(sorted(numbers)), numbers)
                    self.assertTrue(all(1 <= n <= maximum for n in numbers))
                odd = sum(n % 2 for n in results[3][1])
                self.assertIn(odd, [3] if count == 6 else [3, 4])
            out_headers, out_rows = read_csv(export_csv(results, game))
            self.assertEqual(len(out_rows), 5)
            self.assertEqual(len(validate_draws(out_rows, suggest_columns(out_headers, count), game)), 5)

    def test_invalid_numbers(self):
        columns = [f"n{i}" for i in range(1, 7)]
        for values in ([1, 1, 2, 3, 4, 5], [0, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 44], [1, 2, 3, 4, 5, ""], [1, 2, 3, 4, 5, "6.5"]):
            with self.assertRaises(ValueError):
                validate_draws([(2, dict(zip(columns, map(str, values))))], columns, "ロト6")

    def test_csv_validation(self):
        for data in (b"", b"a,a\n1,2", b"a,b\n1", b"a,b\n", b"a,\n1,2", b'a,b\n"unfinished'):
            with self.assertRaises(ValueError):
                read_csv(data)
        data = "本数字1,本数字2\n1,2\n".encode("cp932")
        self.assertEqual(read_csv(data)[0], ["本数字1", "本数字2"])

    def test_recent_window(self):
        old = [(1, 2, 3, 4, 5, 6)] * 50
        recent = [(7, 8, 9, 10, 11, 12)] * 10
        # The recent-only candidate does not depend on older draws.
        from loto import frequencies
        self.assertEqual(frequencies((old + recent)[-10:], 43), frequencies(recent, 43))


if __name__ == "__main__":
    unittest.main()
