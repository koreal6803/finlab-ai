import re
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "skills/finlab/best-practices.md"


def verify_strategy_example():
    text = GUIDE.read_text()
    start = text.index("### ✅ Use `verify_strategy()`")
    section = text[start:text.index("\n---", start)]
    return re.search(r"```python\n(.*?)```", section, re.S).group(1)


class VerifyStrategyGuideTest(unittest.TestCase):
    def test_example_returns_a_report_and_reads_verify_result(self):
        finlab = MagicMock()
        finlab.data.get.return_value.__gt__.return_value = MagicMock()
        report = finlab.backtest.sim.return_value
        result = SimpleNamespace(passed=False, summary_df="summary", details="details")

        def verify_strategy(strategy, n_tests=5):
            self.assertIs(strategy(), report)
            return result

        finlab.verify.verify_strategy = verify_strategy
        modules = {"finlab": finlab, "finlab.data": finlab.data,
                   "finlab.backtest": finlab.backtest, "finlab.verify": finlab.verify}
        namespace = {}
        with patch.dict(sys.modules, modules), patch("builtins.print") as printed:
            exec(verify_strategy_example(), namespace)

        self.assertIs(namespace["result"], result)
        finlab.backtest.sim.assert_called_once_with(ANY, resample="M", upload=False)
        printed.assert_any_call("details")


if __name__ == "__main__":
    unittest.main()
