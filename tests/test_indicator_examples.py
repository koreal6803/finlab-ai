import ast
import re
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "skills/finlab"

# data.indicator() raises ValueError on TA-Lib keywords the indicator does not
# use (finlab >= 2.2.2). Names from talib.abstract.Function(name).parameters.
TALIB_PARAMS = {
    "AD": set(),
    "ADOSC": {"fastperiod", "slowperiod"},
    "ADX": {"timeperiod"},
    "ATR": {"timeperiod"},
    "BBANDS": {"timeperiod", "nbdevup", "nbdevdn", "matype"},
    "EMA": {"timeperiod"},
    "MACD": {"fastperiod", "slowperiod", "signalperiod"},
    "MOM": {"timeperiod"},
    "NATR": {"timeperiod"},
    "OBV": set(),
    "ROC": {"timeperiod"},
    "RSI": {"timeperiod"},
    "SMA": {"timeperiod"},
    "STOCH": {"fastk_period", "slowk_period", "slowk_matype", "slowd_period", "slowd_matype"},
    "TEMA": {"timeperiod"},
    "TRANGE": set(),
    "WILLR": {"timeperiod"},
    "WMA": {"timeperiod"},
}
INDICATOR_KWARGS = {"adjust_price", "resample", "strict", "market"}


def indicator_calls():
    for path in sorted(SKILL.glob("*.md")):
        for block in re.findall(r"```python\n(.*?)```", path.read_text(), re.S):
            try:
                tree = ast.parse(block)
            except SyntaxError:
                continue
            lines = block.splitlines()
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "indicator"
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "data"
                        # Deliberate anti-pattern examples are marked "# ERROR".
                        and "# ERROR" not in lines[node.lineno - 1]):
                    yield path.name, lines[node.lineno - 1].strip(), node


class IndicatorExamplesTest(unittest.TestCase):
    def test_indicator_examples_pass_only_accepted_keywords(self):
        calls = list(indicator_calls())
        self.assertTrue(calls)
        for name, line, node in calls:
            with self.subTest(file=name, line=line):
                indname = node.args[0].value
                self.assertIn(indname, TALIB_PARAMS, "add its TA-Lib parameters to TALIB_PARAMS")
                self.assertEqual(len(node.args), 1)
                kwargs = {kw.arg for kw in node.keywords}
                self.assertLessEqual(kwargs, TALIB_PARAMS[indname] | INDICATOR_KWARGS)


if __name__ == "__main__":
    unittest.main()
