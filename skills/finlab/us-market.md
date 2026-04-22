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
| `us_price:*` (adj_close, volume…)  | Daily      | 2016-01 → present  | ~8,000 tickers  | DatetimeIndex          | `us` (equities)   |
| `us_fund_price:*` (adj_close, volume…) | Daily  | 2016-01 → present  | ~9,300 ETFs/funds | DatetimeIndex        | `us_fund` (ETFs)  |
| `us_income_statement:*`            | Quarterly  | 2015-Q1 → present  | ~5,000 tickers  | `key_date == filing_date` | `us`          |
| `us_balance_sheet:*`               | Quarterly  | 2015-Q1 → present  | ~5,000 tickers  | `key_date == filing_date` | `us`          |
| `us_cash_flow:*`                   | Quarterly  | 2015-Q1 → present  | ~5,000 tickers  | `key_date == filing_date` | `us`          |
| `us_earnings_surprises:*`          | Event-based| 2015-01 → 2025-12  | ~12,000 tickers | DatetimeIndex          | `us`              |
| `us_index_constituents:sp500`      | Daily      | 2022-11 → present  | ~503 tickers    | DatetimeIndex          | `us`              |
| `us_index_constituents:nasdaq100`  | Daily      | 2022-11 → present  | 100 tickers     | DatetimeIndex          | `us`              |
| `world_index:adj_close`            | Daily      | 2015-07 → present  | 35 indices      | DatetimeIndex          | market-agnostic   |

`us_fund_price:*` covers SPY, QQQ, sector SPDRs (XLK / XLF / XLE / …), country ETFs, leveraged/inverse ETFs, and mutual funds. Use it for sector-rotation, ETF momentum, or leveraged-ETF backtests — you must first call `data.set_market('us_fund')` because ETF tickers are not present in `us_price`. See §4.2.

Balance-sheet / cash-flow fields with confirmed coverage (~45 quarters, ~8,600 tickers):
`total_debt`, `total_stockholders_equity`, `net_debt`, `long_term_debt`, `short_term_debt`,
`cash_and_short_term_investments`, `retained_earnings`, `total_liabilities`,
`capital_expenditure`, `stock_based_compensation`, `acquisitions_net`.

Fields **not** populated (check before designing a factor):
`dividends_paid`, `debt_repayment`, `common_stock_issued`, `cash_and_equivalents`.

### 1.2 Current-snapshot-only tables (NOT safe for backtest)

These tables only carry ~16–19 days of recent data. They are live-screening artefacts; using them in backtest is lookahead by construction.

| Table                              | Reason to avoid in backtest                         |
|------------------------------------|-----------------------------------------------------|
| `us_ratios:*` (all columns)        | ~16 days of data, 2026-02-20 → 2026-03-13           |
| `us_key_metrics:*`                 | ~16 days of data                                    |
| `us_analyst_consensus:*`           | ~19 days of data                                    |
| `us_stock_rating:*`                | ~19 days of data                                    |
| `us_dcf:*`                         | ~16 days of data                                    |
| `us_price_target_summary:*`        | ~16 days of data                                    |
| `us_company_profile`               | Static current snapshot (sector, exchange, market_cap) — no history of reclassifications |

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

Quarterly tables use a string index of the form `"<YYYY>-US-Q<N>"`, e.g. `"2024-US-Q3"`. When you combine a quarterly FinlabDataFrame with a daily one (for example, `(quarterly_fcf > 0) & daily_price_condition`), FinLab converts the quarterly index to `DatetimeIndex` using each row's `key_date` and forward-fills — so a quarterly row becomes visible on the daily grid only from the filing date onward. You do not need to call `.shift()` or reassign `.index`. Just combine the DataFrames.

### 1.4 Index-constituent history caveat

`data.us_universe(index='S&P 500')` and `data.us_universe(index='NASDAQ 100')` expose point-in-time membership, but the membership history only begins **2022-11-08**. Backtests that start before that date cannot use point-in-time index membership and must fall back to a dollar-volume or market-cap proxy (see §5.1). For long backtests (2016 onward), this is the single biggest constraint on US universe design.

### 1.5 `us_earnings_surprises` sparsity

Density is ~0.64% (262K non-null cells across 3,415 dates × 12,077 tickers). Post-earnings-announcement-drift (PEAD) strategies that require dense daily surprise data are not viable from this table. Event-based joins (look up a single stock on its announcement date) work fine; rolling cross-sectional factors do not.

---

## 2. Quarterly Alignment (stable, non-obvious)

FinLab aligns US quarterly fundamentals using `key_date == filing_date` (SEC 10-Q filing date), **not** `original_date` (fiscal quarter end). This is the correct, lookahead-safe behaviour and does not require a `.shift()` workaround.

Worked example — AAPL 2024-US-Q3:

| Field           | Value        | Meaning                                      |
|-----------------|--------------|----------------------------------------------|
| `original_date` | 2024-09-28   | Fiscal quarter end                           |
| `filing_date`   | 2024-11-01   | When data became publicly available via SEC  |
| `key_date`      | 2024-11-01   | Used for daily alignment (= `filing_date`)   |

Revenue transitions from Q2 ($85.78B) to Q3 ($94.93B) exactly on 2024-11-01 on the daily grid. Any factor built from `us_income_statement:*`, `us_balance_sheet:*`, or `us_cash_flow:*` inherits this discipline automatically.

**Implication**: Do not call `.shift()` on US quarterly DataFrames to "be safe." The shift is already applied via filing-date alignment, and adding another shift makes the signal trade one period late. Confirmed across all 6,067 US stocks tested.

---

## 3. Report Object API (common confusion)

Backtests on US market return the same `Report` object as Taiwan. Cumulative-return access points:

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
| `tax_ratio`         | 0          | US has no trading stamp duty (unlike Taiwan's 0.3%).   |
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

When the strategy trades tickers such as SPY, QQQ, sector SPDRs, or leveraged ETFs, switch the market to `us_fund`. ETF tickers are **not** in `us_price`, so `sim()` on `us` cannot match them; `us_fund` is the right gate. Typical defaults (same commission-free assumption as equities):

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

### 5.1 Dollar-volume top-N (pre-2022 friendly)

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

### 5.2 Index-constituent membership (post-2022 only)

When point-in-time membership matters (e.g., "S&P 500 only" mandate), use `data.us_universe(index=...)`. The correct index labels are the display strings `'S&P 500'` and `'NASDAQ 100'` (with spaces and ampersand), not `'SP500'` / `'NASDAQ100'`.

```python
from finlab import data

data.set_market('us')
with data.us_universe(index='S&P 500'):
    close = data.get('us_price:adj_close')
    # downstream factor logic operates within S&P 500 members only
```

History starts 2022-11-08. For backtests longer than ~3.4 years, blend with §5.1 (dollar-volume top-N before 2022-11, index membership after).

### 5.3 Quality gates

Stack these on top of §5.1 or §5.2:

| Gate                         | Typical value           | Why                                                                 |
|------------------------------|-------------------------|----------------------------------------------------------------------|
| Minimum price                | `close > 5` (or `> 10`) | Penny stocks have idiosyncratic gaps, wide spreads, and are often untradeable at size. $5 is a widely-accepted floor; raise to $10 if your factor is sensitive to microstructure. |
| Minimum rolling dollar volume| `> $5M / day` (20-day avg) | Ensures you can enter and exit your position size without meaningful slippage. Loosen for small-cap strategies; tighten if holding period is short. |
| Exchange filter              | NYSE / NASDAQ only      | Excludes OTC / pink-sheet listings that have thin, unreliable prints. `us_company_profile:exchange`. |
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

The underlying principle: include a sector if and only if the factor you are computing has the same economic meaning there as elsewhere. `us_company_profile:sector` (static snapshot) is acceptable for this filter despite being point-in-time, because sector reclassifications are rare and typically do not affect the filter's outcome materially.

### 5.5 Data-quality gate for extreme moves

Reverse-split artefacts, ticker reuse, and data-feed errors produce stocks with implausible daily returns (277 stocks have >5 days of 50%+ moves; one shows 9.5 × 10^15 % daily return). Filter them out with a **rolling** rather than full-history check to avoid lookahead:

```python
rets          = close.pct_change()
extreme_today = rets.abs() >= 0.5
# exclude a stock from day T+1 onward once it has shown an extreme move,
# but leave it eligible on all prior days
exclude_mask  = extreme_today.rolling(252, min_periods=1).max().shift(1).fillna(False) > 0
clean_mask    = ~exclude_mask.astype(bool)
```

The rolling-window check excludes a stock only on dates **after** its extreme event. A full-history filter (`rets.abs().max() < 0.5` applied once) inspects the whole series and is lookahead — the stock is excluded on dates **before** the event even though a live strategy could not have known.

---

## 6. Lookahead Bias Checklist (US-specific)

Walk through before every US backtest:

1. **Quarterly alignment.** Are fundamentals coming from `us_income_statement` / `us_balance_sheet` / `us_cash_flow`? Then filing-date alignment is already applied — **do not** `.shift()` on top. (§2)
2. **Current-snapshot data.** Does any column in your factor come from `us_ratios`, `us_analyst_consensus`, `us_stock_rating`, `us_dcf`, `us_price_target_summary`, or `us_key_metrics`? Remove it — these tables carry only ~16–19 days of data. (§1.2)
3. **Universe definition.** Does the universe use any whole-history computation (e.g., `series.max()`, `series.std()` over the full sample)? Rewrite with a rolling window that shifts one day. (§5.5)
4. **Index membership history.** Does the universe rely on `data.us_universe(index='S&P 500' | 'NASDAQ 100')`? Start date must be ≥ 2022-11-08; earlier dates silently return empty membership. (§1.4)
5. **Survivorship.** Does the universe require any field that only exists for currently-listed stocks (e.g., current market cap from `us_company_profile`)? Either drop the filter or replace with a time-series alternative that is safe to look at historically.

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
