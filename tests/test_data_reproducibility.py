import re
import unittest
from pathlib import Path

import pandas as pd


GUIDE = Path(__file__).resolve().parents[1] / "skills/finlab/data-reproducibility.md"
HELPER = next(block for block in re.findall(r"```python\n(.*?)```", GUIDE.read_text(), re.S)
              if "def require_quarter_dates" in block)
namespace = {}
exec(HELPER, namespace)
validate = namespace["require_quarter_dates"]


class QuarterDateCoverageTest(unittest.TestCase):
    def test_each_populated_cell_needs_its_own_date_without_mutating_inputs(self):
        values = pd.DataFrame({"2468": [0., 2.], "6505": [3., float("nan")]},
                              index=["2025-Q1", "2025-Q2"])
        dates = pd.DataFrame({"2468": ["2025-05-15", "2025-08-14"],
                              "6505": ["2025-05-15", None]}, index=values.index)
        date_tables = {"disclosures": dates, "deadlines": dates}
        validate(values, date_tables)
        cases = [dates.iloc[:1], dates.drop(columns="2468")]
        for bad_date in (None, "not-a-date"):
            broken = dates.copy()
            broken.loc["2025-Q1", "2468"] = bad_date
            cases.append(broken)
        original_values, original_dates = values.copy(), dates.copy()
        for broken in cases:
            saved = broken.copy()
            for name in date_tables:
                with self.subTest(name=name, shape=broken.shape):
                    with self.assertRaisesRegex(ValueError, name):
                        validate(values, date_tables | {name: broken})
                    pd.testing.assert_frame_equal(broken, saved)
        pd.testing.assert_frame_equal(values, original_values)
        pd.testing.assert_frame_equal(dates, original_dates)


if __name__ == "__main__":
    unittest.main()
