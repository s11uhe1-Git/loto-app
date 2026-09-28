import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_demo_and_reset(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
        self.assertFalse(at.exception)
        at.checkbox[0].check().run()
        self.assertFalse(at.exception)
        at.button[0].click().run()
        self.assertFalse(at.exception)
        self.assertEqual(len(at.session_state["results"]), 5)
        self.assertTrue(all(len(numbers) == 6 for _, numbers in at.session_state["results"]))
        at.number_input[0].set_value(10).run()
        self.assertNotIn("results", at.session_state)
        at.radio[0].set_value("ロト7").run()
        at.button[0].click().run()
        self.assertFalse(at.exception)
        self.assertTrue(all(len(numbers) == 7 for _, numbers in at.session_state["results"]))
        at.multiselect[0].set_value([]).run()
        self.assertEqual(len(at.error), 1)
        self.assertFalse(at.exception)
