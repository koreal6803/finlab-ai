# US Market Reference

## When to read this

Load this file whenever a strategy targets US markets — both single-stock (`USMarket`) and ETF/fund (`USFundMarket`). Specifically, whenever you see:

- `data.set_market('us')` or `data.set_market('us_fund')`
- `data.get('us_price:...')`, `data.get('us_fund_price:...')`, or any `us_*` / `us_fund_*` table
- `data.us_universe(index='S&P 500' | 'NASDAQ 100')`
- A user question about S&P 500 / NASDAQ 100 / SPY / QQQ / sector ETFs / leveraged ETFs / US equity backtests / 美股

It covers the stable design facts of FinLab's US-market support: what data exists, how it aligns, what the defaults are, and how to bound the universe defensibly — for both single-name equity strategies and ETF / sector-rotation strategies.

This file is intentionally **not** a workaround list for current FinLab bugs — those belong in a separate upstream-bugs log so that when they are fixed the advice here stays correct. The only bug hint that leaks in is §4 (`trade_at_price` recommendation), because the correct default is itself the stable answer.

---

## 1. Data Availability

### 1.1 Backtest-safe tables

These tables carry enough history and point-in-time discipline to be used in a backtest.

| Table                              | Frequency  | History            | Coverage        | Alignment field       | Market            |
|------------------------------------|------------|--------------------|-----------------|------------------------|-------------------|
| `us_price:*` (adj_close, volume…)  | Daily      | 2016-01 → present  | ~10,600 tickers | DatetimeIndex          | `us` (equities)   |
| `us_fund_price:*` (adj_close, volume…) | Daily  | 2016-01 → present  | ~12,100 ETFs/funds | DatetimeIndex       | `us_fund` (ETFs)  |
| `us_income_statement:*`            | Quarterly  | 2015-Q1 → present  | ~10,000 tickers | `key_date` (§2)        | `us`              |
| `us_balance_sheet:*`               | Quarterly  | 2015-Q1 → present  | ~10,000 tickers | `key_date` (§2)        | `us`              |
| `us_cash_flow:*`                   | Quarterly  | 2015-Q1 → present  | ~10,000 tickers | `key_date` (§2)        | `us`              |
| `us_earnings_surprises:*`          | Event-based| 2015-01 → present  | ~12,500 tickers | DatetimeIndex          | `us`              |
| `us_index_constituents:sp500`      | Daily      | 2015-01 → present  | ~503 members/day | DatetimeIndex          | `us`              |
| `us_index_constituents:nasdaq100`  | Daily      | 2015-01 → present  | ~101 members/day | DatetimeIndex          | `us`              |
| `world_index:adj_close`            | Daily      | 2015-07 → present  | 35 indices      | DatetimeIndex          | market-agnostic   |

`us_fund_price:*` covers SPY, QQQ, sector SPDRs (XLK / XLF / XLE / …), country ETFs, leveraged/inverse ETFs, and mutual funds. Use it for sector-rotation, ETF momentum, or leveraged-ETF backtests — you must first call `data.set_market('us_fund')`; see §4.2.

Balance-sheet / cash-flow fields with confirmed coverage:
`total_debt`, `total_stockholders_equity`, `net_debt`, `long_term_debt`, `short_term_debt`,
`cash_and_short_term_investments`, `retained_earnings`, `total_liabilities`,
`capital_expenditure`, `stock_based_compensation`, `acquisitions_net`,
`net_dividends_paid`, `common_stock_issuance`, `net_debt_issuance`.

Field names follow FMP's schema, so guessed names raise `DatasetNotFoundError`:

| Guessed name (does not exist)       | Actual field                                                   |
|-------------------------------------|----------------------------------------------------------------|
| `us_cash_flow:dividends_paid`       | `us_cash_flow:net_dividends_paid` or `us_cash_flow:common_dividends_paid` |
| `us_cash_flow:debt_repayment`       | `us_cash_flow:net_debt_issuance` (net of repayments)           |
| `us_cash_flow:common_stock_issued`  | `us_cash_flow:common_stock_issuance`                           |
| `cash_and_equivalents`              | `us_balance_sheet:cash_and_cash_equivalents`                   |

### 1.2 Current-snapshot-only tables (NOT safe for backtest)

These tables are short-history/current-snapshot data. Firestore catalog currently shows them starting around 2026-02, so they are still 2026-only samples relative to the 2015/2016 history available in price and raw fundamentals. They are live-screening artefacts; using them in long backtests collapses the sample to 2026 and is lookahead by construction.

| Table                              | Reason to avoid in backtest                         |
|------------------------------------|-----------------------------------------------------|
| `us_ratios:*` (all columns)        | Short 2026-only history; catalog starts 2026-02-20 |
| `us_key_metrics:*`                 | Short 2026-only history; catalog starts 2026-02-20 |
| `us_analyst_consensus:*`           | Short 2026-only history; catalog starts 2026-02-24 |
| `us_stock_rating:*`                | Short 2026-only history; catalog starts 2026-02-24 |
| `us_dcf:*`                         | Short 2026-only history; catalog starts 2026-02-24 |
| `us_price_target_summary:*`        | Short 2026-only history; catalog starts 2026-02-24 |
| `us_company_profile`               | Static current snapshot (sector, exchange, market_cap) — no history of reclassifications |

The same FMP snapshot-table families are also short-history in other overseas equity markets: `hk_*`, `jp_*`, `kr_*`, and `uk_*` versions of `ratios`, `key_metrics`, `stock_rating`, `dcf`, and `analyst_consensus`. Treat them as live-screening data, not historical backtest factors.

For a clean US common-stock universe, use `common = data.get('etl:us_common_stock_filter')` then restrict columns with `df = df[df.columns.intersection(common.columns)]`; this excludes ETFs/funds/ADRs/notes/preferreds/warrants/units/rights via `us_company_profile.security_type`. Membership comes from the **current** `us_company_profile` snapshot, so stocks delisted since are excluded: a long backtest restricted to this filter has survivorship bias (§6 #5).

If you need a ratio (P/E, P/B, ROE, debt ratios), **compute it from the raw quarterly statements**. Example:
```python
from finlab import data

data.set_market('us')                                    # session-scope market switch
price = data.get('us_price:adj_close')
eps   = data.get('us_income_statement:eps_diluted')      # quarterly, filing-date aligned
pe    = price / eps.rolling(4).sum()                     # trailing-twelve-months P/E
```

`data.get()` has no `market=` parameter. Select the market in one of two ways:
- **Session-scope**: `data.set_market('us')` or `data.set_market('us_fund')` once, then subsequent `data.get()` calls inherit it. Most common.
- **Explicit table prefix**: call `data.get('us_price:adj_close')` / `data.get('us_fund_price:adj_close')` without changing the session market. Use this when mixing markets in one script.

### 1.3 Quarterly index-format convention

Quarterly tables use a string index of the form `"<YYYY>-US-Q<N>"`, e.g. `"2024-US-Q3"`. Keep pure quarterly calculations on that string index; for example, `roe = net_income / equity` is correct and should not be manually converted first. When that quarterly result is later combined with daily data through FinlabDataFrame operators or boolean indexing, FinLab's internal `reshape()` calls `index_str_to_date()` automatically, converts rows by `key_date` / filing date, and forward-fills onto the combined daily grid. You do not need to call `.index_str_to_date()`, `.reindex(close.index, method='ffill')`, `.shift()`, or manually reassign `.index` for normal factor construction. Use `.index_str_to_date()` only when you explicitly need a dated index object, such as extracting disclosure-date rows or doing pandas-native operations outside FinlabDataFrame alignment.

### 1.4 Index-constituent history caveat

`us_index_constituents:sp500` and `us_index_constituents:nasdaq100` are daily boolean membership tables starting **2015-01-02** (True = index member that day), so they cover the whole `us_price` history. `data.us_universe(index=...)` does **not** use that history: it takes the table's **latest** row and applies today's members to every historical date, which builds survivorship and look-ahead bias into any backtest run inside it. For historical membership, mask with `us_index_constituents:*` (§5.2).

The S&P 500 history before 2022-11-08 is rebuilt from archived Wikipedia snapshots carried forward between observations (median gap 8 days, max 36), so a membership change can be dated up to a few weeks off its effective date; from 2022-11-08 it is a daily snapshot. NASDAQ 100 dates follow recorded index changes. The mask removes survivorship bias but is not an exact effective-date record.

### 1.5 `us_earnings_surprises` sparsity

Density is ~0.61% (280K non-null cells across 3,643 dates × 12,541 tickers, as of 2026-10). Post-earnings-announcement-drift (PEAD) strategies that require dense daily surprise data are not viable from this table. Event-based joins (look up a single stock on its announcement date) work fine; rolling cross-sectional factors do not.

---

## 2. Quarterly Alignment (stable, non-obvious)

FinLab aligns US quarterly fundamentals on `key_date`, **not** `original_date` (fiscal quarter end). This is the correct, lookahead-safe behaviour and does not require a `.shift()` workaround.

- When FMP supplies the real SEC filing date, `key_date == filing_date`.
- About 23% of (quarter, stock) rows only carry a placeholder `filing_date` equal to the period end (or the day after). For those, `key_date` = period end + filing deadline: 45 days for a US company's 10-Q, 90 days for its 10-K, 120 days for filers without a US deadline (foreign issuers, funds).

`key_date` is the right date for backtest alignment. For an event study that needs the actual disclosure date, neither column has it on placeholder rows: `filing_date` is the period end (too early) and `key_date` is the deadline (the latest possible date). Keep only rows where `data.get('us_income_statement:key_date')` equals `data.get('us_income_statement:filing_date')`, or treat the others as estimated dates.

Worked example — AAPL 2024-US-Q3:

| Field           | Value        | Meaning                                      |
|-----------------|--------------|----------------------------------------------|
| `original_date` | 2024-09-28   | Fiscal quarter end                           |
| `filing_date`   | 2024-11-01   | When data became publicly available via SEC  |
| `key_date`      | 2024-11-01   | Used for daily alignment (= real `filing_date`) |

Revenue transitions from Q2 ($85.78B) to Q3 ($94.93B) exactly on 2024-11-01 on the daily grid. Any factor built from `us_income_statement:*`, `us_balance_sheet:*`, or `us_cash_flow:*` inherits this discipline automatically.

**Implication**: Do not call `.shift()` on US quarterly DataFrames to "be safe." The delay is already applied via `key_date` alignment, and adding another shift makes the signal trade one period late.

---

## 3. Report Object API (common confusion)

Backtests on US market return the same `Report` object as other markets. Cumulative-return access points:

| Attribute / method          | Returns                                              |
|-----------------------------|------------------------------------------------------|
| `report.creturn`            | Cumulative return Series (1.0-indexed)               |
| `report.daily_creturn`      | Daily cumulative return Series                       |
| `report.get_stats()`        | Dict with `cagr`, `monthly_sharpe`, `max_drawdown`, … |
| `report.metrics.annual_return()` | Annualised return (float)                       |
| `report.metrics.sharpe_ratio()`  | Sharpe (float)                                  |
| `report.metrics.max_drawdown()`  | MDD (float)                                     |

There is **no** `report.get_equity()` method. The common mistake is to assume it exists (analogous naming in other libraries); use `report.creturn` instead.

---

## 4. Backtest Defaults

Two distinct US markets: **`us`** (single-name equities via `USMarket`) and **`us_fund`** (ETFs / mutual funds via `USFundMarket`). Pick the market once with `data.set_market(...)` and the matching defaults apply automatically.

### 4.1 Single-name equities (`USMarket`)

Defaults (activated by `data.set_market('us')`):

| Parameter           | Default    | Why                                                    |
|---------------------|-----------:|--------------------------------------------------------|
| `fee_ratio`         | 0          | Commission-free brokers (Robinhood, IBKR Lite, Fidelity) are the common case. |
| `tax_ratio`         | 0          | US has no trading stamp duty (unlike TW market's 0.3%). |
| `trade_at_price`    | `'close'`  | Close-price execution is the safe choice for US.       |

Override `fee_ratio` only when modelling a broker that charges per-share fees (IBKR Pro, legacy brokers). Leave `tax_ratio` at 0; short-term-vs-long-term capital-gains tax is a portfolio-accounting concern, not a per-trade simulation parameter.

For ranking-based strategies, pair `sim()` with `resample='W'` (or `'M'`) to avoid churn from day-to-day rank fluctuation:
```python
from finlab import data
from finlab.backtest import sim

data.set_market('us')                           # US single-stock market
close = data.get('us_price:adj_close')
vol   = data.get('us_price:volume')

momentum = close / close.shift(126) - 1         # ~6-month momentum
position = momentum.is_largest(20)              # hold top-20
report   = sim(position, resample='W')          # fee/tax/trade_at_price come from USMarket
```

### 4.2 ETFs and funds (`USFundMarket`)

When the strategy trades tickers such as SPY, QQQ, sector SPDRs, or leveraged ETFs, switch the market to `us_fund`. These major ETFs are **not** in `us_price`, so `sim()` on `us` cannot match them; `us_fund` is the right gate. Typical defaults (same commission-free assumption as equities):

| Parameter           | Default    | Why                                                    |
|---------------------|-----------:|--------------------------------------------------------|
| `fee_ratio`         | 0          | ETF trading is commission-free on the common US brokers. |
| `tax_ratio`         | 0          | No trading stamp duty.                                   |
| `trade_at_price`    | `'close'`  | Close-price execution; same rationale as equities.      |

Sector-rotation example — hold the strongest of SPY/QQQ each month:
```python
from finlab import data
from finlab.backtest import sim

data.set_market('us_fund')                      # switch to ETF/fund market
close = data.get('us_fund_price:adj_close')

momentum = close[['SPY', 'QQQ']].pct_change(126)
position = momentum.is_largest(1)               # hold the single strongest ETF
report   = sim(position, resample='M')
```

Do not mix the two markets in one `sim()` call: pick equities **or** ETFs. Run them as separate strategies if you want to blend them in a portfolio, then combine the reports.

---

## 5. US Universe Construction

A defensible US universe isolates stocks that are (a) tradeable at meaningful size, (b) priced above noise thresholds, and (c) free of data artefacts. FinLab gives you two starting points — index membership and dollar-volume ranking — and both need quality gates on top.

### 5.1 Dollar-volume top-N

The most portable pattern. Rank stocks by rolling average dollar volume and keep the top-N. Works back to 2016 without needing index-membership history.

```python
from finlab import data

data.set_market('us')
close  = data.get('us_price:adj_close')
volume = data.get('us_price:volume')

dollar_vol = (close * volume).rolling(60, min_periods=20).mean()
top_100    = dollar_vol.is_largest(100)     # top-100 per day
```

Why 60-day rolling: absorbs earnings-day volume spikes; a 20-day window lets a single earnings date dominate; a 250-day window is too slow to capture rotation into a newly-liquid stock.

Why `min_periods=20`: allows freshly-listed stocks to enter the universe after ~1 month of trading instead of waiting a full 60 days.

Why top-100 rather than top-500: concentrates the strategy on names where (i) adjusted price series are clean, (ii) execution slippage is minimal, and (iii) idiosyncratic events are less likely to dominate returns. Widen if your factor explicitly targets small/mid caps.

### 5.2 Index-constituent membership

When point-in-time membership matters (e.g., "S&P 500 only" mandate), mask the factor with the daily `us_index_constituents:*` table so each date ranks only that day's members:

```python
from finlab import data
from finlab.backtest import sim

data.set_market('us')
close    = data.get('us_price:adj_close')
in_sp500 = data.get('us_index_constituents:sp500')   # daily bool: True = member that day

momentum = close / close.shift(126) - 1
position = momentum[in_sp500].is_largest(20)          # rank only that day's S&P 500 members
report   = sim(position, resample='M')
```

Use `us_index_constituents:nasdaq100` for NASDAQ 100. Tickers are matched exactly, so a renamed ticker or one missing from `us_price` drops out.

`data.us_universe(index='S&P 500' | 'NASDAQ 100')` is **not** point-in-time (§1.4): use it only to screen current members, never to define a backtest universe.

### 5.3 Quality gates

Stack these on top of §5.1 or §5.2:

| Gate                         | Typical value           | Why                                                                 |
|------------------------------|-------------------------|----------------------------------------------------------------------|
| Minimum price                | `close > 5` (or `> 10`) | Penny stocks have idiosyncratic gaps, wide spreads, and are often untradeable at size. $5 is a widely-accepted floor; raise to $10 if your factor is sensitive to microstructure. |
| Minimum rolling dollar volume| `> $5M / day` (20-day avg) | Ensures you can enter and exit your position size without meaningful slippage. Loosen for small-cap strategies; tighten if holding period is short. |
| Exchange filter              | NYSE / NASDAQ only      | Excludes OTC / pink-sheet listings that have thin, unreliable prints. `exchange` column of `data.get('us_company_profile')` (current snapshot). |
| ETF / fund exclusion         | `is_etf == False & is_fund == False` | Under `data.set_market('us')` you want single-name equities only — exclude ETFs/funds here. For ETF or sector-rotation strategies, do the opposite: switch to `data.set_market('us_fund')` and trade from `us_fund_price:*` (see §4.2). |

### 5.4 Sector filters (methodology, not a rule)

Sector exclusion is a **factor-specific** decision, not a universal recommendation. Think in terms of whether a factor's premise survives in a given sector:

| Sector              | When to exclude                                           | Rationale                                                                 |
|---------------------|----------------------------------------------------------|---------------------------------------------------------------------------|
| Financial Services  | Always, for most equity factors                          | SPAC- and holding-company-heavy; balance sheet is not comparable to operating companies. |
| Healthcare          | Momentum / trend strategies                              | Binary FDA events cause discontinuous jumps that do not persist as trends. Keep when combined with quality filters (positive FCF, improving EPS) that force profitable-biotech selection. |
| Energy              | Cross-sectional quality / momentum strategies            | Returns are dominated by a common commodity factor (oil, natural gas); cross-sectional ranking is weak. Keep when explicitly running a commodity-beta or sector-rotation strategy. |
| Utilities           | Momentum, risk-on strategies                             | Low-beta, rate-sensitive; momentum premium is weak. Keep for defensive / quality strategies. |
| Real Estate (REITs) | Accounting-quality factors                               | REIT capital structure (pass-through income, heavy leverage) makes standard quality ratios incomparable to operating companies. |

The underlying principle: include a sector if and only if the factor you are computing has the same economic meaning there as elsewhere. The `sector` column of `data.get('us_company_profile')` is acceptable for this filter despite being a current snapshot, because sector reclassifications are rare and typically do not affect the filter's outcome materially.

### 5.5 Data-quality gate for extreme moves

Reverse-split artefacts, ticker reuse, and data-feed errors produce stocks with implausible daily returns (hundreds of tickers have more than five days of ±50% moves; the largest single-day return exceeds 10^9 %). Filter them out with a **rolling** rather than full-history check to avoid lookahead:

```python
rets          = close.pct_change()
extreme_today = rets.abs() >= 0.5
# exclude a stock from day T+1 onward once it has shown an extreme move,
# but leave it eligible on all prior days
exclude_mask  = extreme_today.rolling(252, min_periods=1).max().shift(1) > 0
clean_mask    = ~exclude_mask.astype(bool)
```

The rolling-window check excludes a stock only on dates **after** its extreme event. A full-history filter (`rets.abs().max() < 0.5` applied once) inspects the whole series and is lookahead — the stock is excluded on dates **before** the event even though a live strategy could not have known.

---

## 6. Lookahead Bias Checklist (US-specific)

Walk through before every US backtest:

1. **Quarterly alignment.** Are fundamentals coming from `us_income_statement` / `us_balance_sheet` / `us_cash_flow`? Then filing-date alignment is already applied — **do not** `.shift()` on top. (§2)
2. **Current-snapshot data.** Does any column in your factor come from `us_ratios`, `us_analyst_consensus`, `us_stock_rating`, `us_dcf`, `us_price_target_summary`, or `us_key_metrics`? Remove it — these tables are short-history 2026-only samples in the catalog. (§1.2)
3. **Universe definition.** Does the universe use any whole-history computation (e.g., `series.max()`, `series.std()` over the full sample)? Rewrite with a rolling window that shifts one day. (§5.5)
4. **Index membership history.** Does the universe rely on `data.us_universe(index=...)`? It applies today's members to every date; replace it with the `us_index_constituents:*` mask. (§1.4, §5.2)
5. **Survivorship.** Does the universe require any field that only exists for currently-listed stocks (e.g., `etl:us_common_stock_filter`, or current market cap from `us_company_profile`)? Either drop the filter or replace with a time-series alternative that is safe to look at historically.

A quick sanity check: re-run your strategy after rolling the universe definition back by a year (i.e., treat the data as if it ended one year ago). If returns drop noticeably and the missing year was normal (not a crash), you almost certainly have a lookahead in universe construction.

---

## 7. Cross-references

- FinlabDataFrame methods (`is_largest`, `rank`, `sustain`, `rolling`, `rise`):
  [dataframe-reference.md](dataframe-reference.md)
- `sim()` full signature, `Report` class, metrics mapping:
  [backtesting-reference.md](backtesting-reference.md)
- General lookahead prevention (non-US-specific anti-patterns):
  [best-practices.md](best-practices.md)
- Factor IC, Shapley values, `calc_metric`:
  [factor-analysis-reference.md](factor-analysis-reference.md)
- Factor syntax templates and examples:
  [factor-examples.md](factor-examples.md) — see "US Equity Examples" section
