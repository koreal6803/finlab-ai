import re
import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch


class VerifyStrategyGuideTest(unittest.TestCase):
    def test_example_returns_a_report_and_reads_verify_result(self):
        guide = Path(__file__).resolve().parents[1] / "skills/finlab/backtesting-reference.md"
        section = guide.read_text().split("## Lookahead Bias Self-Check", 1)[1].split("\n---", 1)[0]
        code = re.search(r"```python\n(.*?)```", section, re.S).group(1)
        data = ModuleType("finlab.data")
        data.get = MagicMock(return_value=MagicMock())
        backtest = ModuleType("finlab.backtest")
        report = SimpleNamespace(trades=[])
        backtest.sim = MagicMock(return_value=report)
        verify = ModuleType("finlab.verify")
        result = SimpleNamespace(passed=True, summary_df="summary", details=[])

        def verify_strategy(strategy, n_tests=5):
            self.assertIs(strategy(), report)
            self.assertEqual(strategy().trades, [])
            return result

        verify.verify_strategy = verify_strategy
        finlab = ModuleType("finlab")
        finlab.data = data
        with patch.dict(sys.modules, {"finlab": finlab, "finlab.data": data,
                                     "finlab.backtest": backtest, "finlab.verify": verify}):
            namespace = {}
            with patch("builtins.print"):
                exec(compile(code, str(guide), "exec"), namespace)
        self.assertIs(namespace["result"], result)
        self.assertEqual(backtest.sim.call_count, 2)
        self.assertTrue(all(call.kwargs == {"resample": "M", "upload": False}
                            for call in backtest.sim.call_args_list))
        self.assertGreaterEqual(data.get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
