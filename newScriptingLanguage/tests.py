import io
import contextlib
import unittest

from hackscript import run


class HackScriptTests(unittest.TestCase):
    def execute(self, source: str) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            run(source)
        return buf.getvalue().strip()

    def test_arithmetic_and_print(self):
        out = self.execute("let a = 10; let b = 4; print a * b + 2;")
        self.assertEqual(out, "42")

    def test_if_else(self):
        out = self.execute(
            "let score = 88; if (score >= 90) { print \"A\"; } else { print \"B\"; }"
        )
        self.assertEqual(out, "B")

    def test_while_loop(self):
        out = self.execute(
            "let i = 1; let sum = 0; while (i <= 3) { sum = sum + i; i = i + 1; } print sum;"
        )
        self.assertEqual(out, "6")


if __name__ == "__main__":
    unittest.main()
