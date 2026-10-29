# Historical Versions and Reproducible Inputs

These examples target the released **finlab 2.2.22** API. Updating this Skill changes guidance; it does not update the installed Python package or repair cached data. Install the example environment with `uv pip install "finlab==2.2.22"` and use the supported [login flow](SKILL.md#prerequisites) for online reads.

## Select a published version of each table

`data.versions(dataset: str) -> pd.DataFrame` lists retained publications, oldest first. It requires a paid data plan. Columns are `generation`, `time_created`, `time_replaced` (UTC; `NaT` means still published), `size` (bytes), and `hash`.

The keyword-only `data.get` selectors are:

| Parameter | Default | Meaning |
| --- | --- | --- |
| `as_of` | `None` | Date/time selecting the table publication active then; not a cutoff on its rows. Naive times use Asia/Taipei for every market; a bare date means 00:00. |
| `version` | `None` | Exact `str` or `int` generation returned by `data.versions`. Mutually exclusive with `as_of`. |

Historical downloads count toward the download quota; already downloaded generations can be cached. These selectors cannot be combined with `start`, `end`, or progress reporting, and do not support intraday tables. Slice the returned frame afterward if needed. Online selection can only retrieve publications the server still retains; an unavailable publication raises an error. Do not silently substitute the latest table.

```python
from finlab import data

dataset = "price:收盤價"
publications = data.versions(dataset)
print(publications)
if publications.empty:
    raise RuntimeError("No retained publication; stop this run")

# Choose an actual retained timestamp instead of assuming an old date exists.
latest = publications.iloc[-1]
published_at = latest["time_created"]
generation = str(latest["generation"])
close_at_time = data.get(dataset, as_of=published_at)
close_exact = data.get(dataset, version=generation)
```

**Each table is selected independently.** `data.get(..., as_of=...)` does not set a session-wide date. Later `deadline()`, `index_str_to_date()`, automatic quarterly/daily alignment, `sim()`, and report calculations may read other tables at their current versions. Record the complete computation below; if reconstructing historical publications, choose versions for every dependency explicitly. A common timestamp does not make separately published tables an atomic or certified consistent release.

`financial_statement:*` uses permanent vintages instead of these short-lived publication versions. Inspect `data.get("financial_statement_versions")` and read a dataset named in its `dataset` column. Its date dependencies still need separate selection and validation.

## Check Taiwan quarterly date coverage before computing

For every non-null financial value, require a valid date for the **same stock and quarter**. A nonempty date table or a matching latest quarter does not catch individual missing cells or columns. For Taiwan `deadline()`, check both `etl:financial_statements_disclosure_dates` and `etl:financial_statements_deadline`; the former is also needed to avoid using late filings before publication. Taiwan date conversion also reads `price:收盤價` for trading-day and stopped-stock handling. Other markets have different date keys; see [us-market.md](us-market.md).

The following helper validates raw quarterly inputs. Its pandas `reindex` is only a coverage check; it does not align strategy signals or replace FinLab's date conversion.

```python
import pandas as pd


def require_quarter_dates(
    values: pd.DataFrame, date_tables: dict[str, pd.DataFrame]
) -> None:
    """Raise ValueError for populated stock/quarter cells without valid dates."""
    populated = pd.DataFrame(values).notna()
    for name, dates in date_tables.items():
        covered = pd.DataFrame(dates).reindex(
            index=populated.index, columns=populated.columns
        ).apply(pd.to_datetime, errors="coerce", format="ISO8601")
        missing = (populated & covered.isna()).stack()
        gaps = missing[missing].index.tolist()
        if gaps:
            raise ValueError(f"{name}: missing (quarter, stock) dates: {gaps[:10]}")
```

Synchronize the financial values and their date dependencies while online, then validate them **before** conversion, backtesting, or replacing any accepted exports. If validation fails, stop the entire batch and keep the previous accepted snapshot/output files. Retain the failed inputs for diagnosis and retry synchronization in a new snapshot directory. Do not invent announcement dates, fill missing dates from another quarter, forward-fill a date table, or overwrite the original financial files.

**Known behavior in 2.2.22:** incomplete offline date tables can silently leave an older quarter in the converted result. This helper stops such a run; upgrading to 2.2.22 alone does not add a missing-quarter warning. Coverage is a necessary check, not proof that a supplied date is correct or that all tables were published together.

## Record and strictly replay a complete strategy

`data.snapshot(path: str | Path, *, mode: str = "record")` is a context manager yielding the resolved snapshot `Path`.

- `record` requires a **new directory**. It saves every `data.get`/`data.gets` result read inside the block, including internal dependencies. `manifest.json` is committed only when the block succeeds.
- `replay` reads those saved inputs, without falling back to ordinary caches or newer data. Missing inputs, different selections, missing files, or mismatched environment versions fail. Keep the market, universe, truncation settings, and read arguments the same.
- Keep the same Python, finlab, pandas, NumPy, and PyArrow versions recorded in `manifest.json`. Archive the strategy source, parameters, fixed `end_date`, environment lockfile, and outputs separately. Only load your own trusted snapshots: input files use pickle.

Save the coverage helper above and the following code in the same Python script. `run_strategy` explicitly reads and validates the two date tables, then `deadline()` and `sim()` record their additional reads. `force_download=True` synchronizes the explicit financial/date/price reads during online recording.

```python
from pathlib import Path
from finlab import data
from finlab.backtest import sim


def run_strategy(force_download: bool = False):
    cash = data.get(
        "financial_statement:現金及約當現金", force_download=force_download
    )
    date_tables = {
        key: data.get(key, force_download=force_download)
        for key in (
            "etl:financial_statements_disclosure_dates",
            "etl:financial_statements_deadline",
        )
    }
    require_quarter_dates(cash, date_tables)
    close = data.get("price:收盤價", force_download=force_download)
    position = (cash.deadline() > 0) & (close > close.average(60))
    return sim(position, resample="M", end_date="2025-12-31", upload=False)


data.set_market("tw")
folder = Path("cash-snapshot-2026-10-29")  # must not already exist

# Online: no preloaded strategy DataFrames outside this block.
with data.snapshot(folder, mode="record"):
    recorded = run_strategy(force_download=True)
    recorded_stats = recorded.get_stats()
    recorded.to_html("cash-recorded.html")

# Replay saved data; sim() may still need online backtest authorization.
with data.snapshot(folder, mode="replay"):
    replayed = run_strategy()
    replayed_stats = replayed.get_stats()
    replayed.to_html("cash-replayed.html")

print(recorded_stats["cagr"], replayed_stats["cagr"])
```

For a later session, load the helper and function definitions and run **only the replay block** against the saved folder; do not rerun recording into that folder. Saved data can be replayed offline, but `sim()` authorization is outside the snapshot: a fresh process or expired authorization may need a connection. Do not assume a cold offline backtest will work. `LazyWide` expressions must be evaluated inside the block too: use `sim()` there, or call `.collect()` there when using pandas operations. See [SKILL.md](SKILL.md#performance-defaults).

To check strict failure, this separate replay deliberately asks for a selection the example did not record:

```python
from finlab import data

try:
    with data.snapshot("cash-snapshot-2026-10-29", mode="replay"):
        data.get("price:收盤價", start="2025-01-01")
except ValueError as exc:
    print(exc)  # Snapshot input unavailable; do not retry with current data.
else:
    raise AssertionError("Expected the unrecorded selection to fail")
```

**Capture boundaries:** data read before the block, external APIs/files, and work evaluated after the block are not captured. Neither `data.versions()` queries nor arbitrary network operations are a snapshot of strategy inputs. Avoid overlapping snapshot blocks and finish all worker threads before leaving one. `upload=False` avoids backtest uploads; other code may still use network services. A snapshot preserves what was actually read, including stale or inconsistent inputs; it cannot recover an expired publication that was never saved and does not certify cross-table consistency. Run coverage validation before accepting the recording.

API source: [released finlab 2.2.22](https://pypi.org/project/finlab/2.2.22/), [official upgrade guide](https://finlab.finance/docs/upgrade-guide/).
