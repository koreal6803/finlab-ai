---
name: finlab
description: Comprehensive guide for FinLab quantitative trading package across global stock markets (TW, US, KR, JP, HK; both single-name equities and ETFs/funds). Use when working with trading strategies, backtesting, stock data, FinLabDataFrame, factor analysis, stock selection, or when the user mentions FinLab, trading, quant trading, US equity, S&P 500 / NASDAQ 100, SPY / QQQ, sector or leveraged ETFs, ETF rotation, 美股, or stock market analysis. Includes data access, strategy development, backtesting workflows, best practices, and US-market specifics (data availability map, filing-date-aligned quarterly fundamentals, US universe construction, USMarket vs. USFundMarket defaults, and ETF backtesting).
compatibility: Requires Python 3.10+ and uv package manager (https://docs.astral.sh/uv/)
---

# FinLab Quantitative Trading Package

## Prerequisites

**Before running any FinLab code, verify these in order:**

1. **uv is installed** (Python package manager):

   ```bash
   uv --version
   ```

   If uv is not installed, tell the user to install it.

   After installing, ensure `uv` is on PATH:

   ```bash
   source $HOME/.local/bin/env 2>/dev/null  # Add uv to current shell
   ```

2. **FinLab is installed via uv** (requires >= 2.0.0):

   ```bash
   uv python install 3.12  # Ensure Python is available (skip if already installed)
   uv pip install --system "finlab>=2.0.0" 2>/dev/null || uv pip install "finlab>=2.0.0"
   ```

   **Or use `uv run` for zero-setup execution** (recommended for one-off scripts):

   ```bash
   uv run --with "finlab" python3 script.py
   ```

   `uv run --with` auto-creates a temporary environment with dependencies — no venv management needed.

   **Prefer zero-install?** Run notebooks directly in [FinLab Studio](https://studio.finlab.finance) — a hosted Jupyter environment with `finlab` preinstalled and your account already logged in.

3. **Logged in to FinLab** (finlab >= 2.0; no legacy API token required):

   **Desktop (has a browser):** log in once; credentials are cached locally:

   ```bash
   python -m finlab login
   ```

   ```python
   import finlab
   finlab.login()  # reuses cached credentials, or starts browser login if none
   ```

   **Headless / cron / Docker:** on a machine with a browser, log in and run:

   ```bash
   python -m finlab token --env
   ```

   Set all three exported variables — `FINLAB_REFRESH_TOKEN`, `FINLAB_SESSION_ID`, and `FINLAB_API_KEY` — in the headless environment. FinLab uses them automatically. Treat the output as credentials: use your platform's secret storage and do not paste it into chat or commit it.

   **Google Colab:** run `finlab.login()` in a cell and follow the login link.

   **Migrating from legacy tokens:** `FINLAB_API_TOKEN` and `finlab.login('<api_token>')` are deprecated. Run `python -m finlab migrate`, set up browser login or the three environment variables above, then remove the old token from your configuration.

   **Legacy-token status:** No removal version or date is publicly confirmed in the [official authentication guide](https://finlab.finance/docs/reference/finlab/); the `2026/08/01` date in client warning text is not a removal announcement. Dropping the **client-side** fallback and rejecting legacy tokens **server-side** are separate changes, and a cached `data.get()` call does not test server authentication — use the supported login flow above.

## Language

**Respond in the user's language.** If user writes in Chinese, respond in Chinese. If in English, respond in English.

## Market Support

FinLab supports TW (default), US, KR, JP, HK, plus Taiwan emerging (`rotc`) and Taiwan convertible bonds (`tw_cb`). Pick the market once per session with `data.set_market(<code>)`; generic dataset names like `price:收盤價` or `monthly_revenue:當月營收` resolve to the active market's tables, so strategy code is written the same way across markets. `data.set_market('rotc')` *(v2.0.9)* enables 興櫃 (TW emerging) — use it when you need pre-listing price action or revenue factors that don't exist in the main TSE/OTC catalog.

The rest of this file plus [dataframe-reference.md](dataframe-reference.md), [backtesting-reference.md](backtesting-reference.md), [best-practices.md](best-practices.md), [factor-analysis-reference.md](factor-analysis-reference.md), and [machine-learning-reference.md](machine-learning-reference.md) are **market-agnostic** — the APIs behave the same across markets.

For US-market work — whether single-name equities (`data.set_market('us')`) or ETFs/funds (`data.set_market('us_fund')`) — **read [us-market.md](us-market.md) first**. Queries that should trigger it include: US equity, S&P 500, NASDAQ 100, 美股, SPY / QQQ, sector SPDRs, leveraged / inverse ETFs, ETF rotation, `us_price:*`, `us_fund_price:*`, `data.us_universe(...)`, or `us_income_statement:*` / `us_cash_flow:*` / `us_balance_sheet:*`. It documents:

- Which US data tables are safe for backtesting versus current-snapshot-only (analyst consensus, ratios, DCF are live-only — do not use them historically)
- Filing-date-aligned quarterly fundamentals (`key_date == filing_date`) — no `.shift()` workaround needed
- `Report` API names on US (`creturn` / `daily_creturn` / `get_stats()`; no `get_equity()`)
- US backtest defaults for both markets: `USMarket` (`fee_ratio=0`, `tax_ratio=0`, `trade_at_price='close'`) and `USFundMarket` for ETF/fund backtests
- How `data.set_market(...)` is the session-scope switch (there is no `market=` kwarg on `data.get()`)
- Dollar-volume-top-N universe construction (works back to 2016), S&P 500 / NASDAQ 100 membership via `data.us_universe(index='S&P 500' | 'NASDAQ 100')` with its 2022-11 history-start caveat, quality gates, and sector-exclusion rationale
- Lookahead-bias checklist specific to US data (rolling-window universe filters, survivorship avoidance)
- ETF / sector-rotation backtesting via `USFundMarket` and `us_fund_price:*`

Other-market queries can skip that file.

## Account Tiers & Usage

### Tiers

| Tier | Daily Limit |
| ---- | ----------- |
| Free | 500 MB      |
| VIP  | 5000 MB     |

Check the current plan and quota with `python -m finlab status`.


### Usage Reset

- Resets daily at **8:00 AM UTC+8**
- When limit exceeded, user must wait for reset or upgrade to VIP at [finlab.finance](https://finlab.finance)


## Quick Start Example

```python
from finlab import data
from finlab.backtest import sim

# 1. Fetch data
close = data.get("price:收盤價")
vol = data.get("price:成交股數")
pb = data.get("price_earning_ratio:股價淨值比")

# 2. Create conditions
cond1 = close.rise(10)  # Rising last 10 days
cond2 = vol.average(20) > 1000*1000  # High liquidity
cond3 = pb.rank(axis=1, pct=True) < 0.3  # Low P/B ratio

# 3. Combine conditions and select stocks
position = cond1 & cond2 & cond3
position = pb[position].is_smallest(10)  # Top 10 lowest P/B

# 4. Backtest
report = sim(position, resample="M", upload=False)

# 5. Print metrics - Two equivalent ways:

# Option A: Using metrics object
print(report.metrics.annual_return())
print(report.metrics.sharpe_ratio())
print(report.metrics.max_drawdown())

# Option B: Using get_stats() dictionary (different key names!)
stats = report.get_stats()
print(f"CAGR: {stats['cagr']:.2%}")
print(f"Sharpe: {stats['monthly_sharpe']:.2f}")
print(f"MDD: {stats['max_drawdown']:.2%}")

# Benchmark stats (finlab >= 2.0.17): same keys via report.get_benchmark_stats()

# 6. Write the FinLab-generated HTML report (REQUIRED — do not hand-roll your own HTML)
report.to_html("report.html")
print("Open report.html to inspect equity curve, monthly returns, drawdown, and trade list.")
```

## Core Workflow: 5-Step Strategy Development

### Step 1: Fetch Data

Use `data.get("<TABLE>:<COLUMN>")` to retrieve data:

```python
from finlab import data

# Price data
close = data.get("price:收盤價")
volume = data.get("price:成交股數")

# Financial statements
roe = data.get("fundamental_features:ROE稅後")
revenue = data.get("monthly_revenue:當月營收")

# Valuation
pe = data.get("price_earning_ratio:本益比")
pb = data.get("price_earning_ratio:股價淨值比")

# Institutional trading
foreign_buy = data.get("institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)")

# Technical indicators
rsi = data.indicator("RSI", timeperiod=14)
macd, macd_signal, macd_hist = data.indicator("MACD", fastperiod=12, slowperiod=26, signalperiod=9)
```

**Filter by market/category using `data.universe()`:**

```python
# Limit to specific industry
with data.universe(market='TSE_OTC', category=['水泥工業']):
    price = data.get('price:收盤價')

# Set globally
data.set_universe(market='TSE_OTC', category='半導體')
```

Use `data.search('keyword', market='<market>')` to discover available datasets. Supported markets: `tw`, `us`, `kr`, `jp`, `hk`. Use keywords in the dataset's native language (e.g. `data.search('營收', market='tw')`, `data.search('revenue', market='us')`).

### Step 2: Create Factors & Conditions

Use FinLabDataFrame methods to create boolean conditions:

```python
# Trend
rising = close.rise(10)  # Rising vs 10 days ago
sustained_rise = rising.sustain(3)  # Rising for 3 consecutive days

# Moving averages
sma60 = close.average(60)
above_sma = close > sma60

# Ranking
top_market_value = data.get('etl:market_value').is_largest(50)
low_pe = pe.rank(axis=1, pct=True) < 0.2  # Bottom 20% by P/E

# Industry ranking
industry_top = roe.industry_rank() > 0.8  # Top 20% within industry
```

See [dataframe-reference.md](dataframe-reference.md) for all FinLabDataFrame methods.

### Step 3: Construct Position DataFrame

Combine conditions with `&` (AND), `|` (OR), `~` (NOT):

```python
# Simple position: hold stocks meeting all conditions
position = cond1 & cond2 & cond3

# Limit number of stocks
position = factor[condition].is_smallest(10)  # Hold top 10

# Entry/exit signals with hold_until
entries = close > close.average(20)
exits = close < close.average(60)
position = entries.hold_until(exits, nstocks_limit=10, rank=-pb)
```

**Important:** Position DataFrame should have:

- **Index**: DatetimeIndex (dates)
- **Columns**: Stock IDs (e.g., '2330', '1101')
- **Values**: Boolean (True = hold) or numeric (position size)

### Step 4: Backtest

```python
from finlab.backtest import sim

# Basic backtest
report = sim(position, resample="M")

# With risk management
report = sim(
    position,
    resample="M",
    stop_loss=0.08,
    take_profit=0.15,
    trail_stop=0.05,
    position_limit=1/3,
    fee_ratio=1.425/1000/3,
    tax_ratio=3/1000,
    trade_at_price='open',
    upload=False
)

# Extract metrics - Two ways:
# Option A: Using metrics object
print(f"Annual Return: {report.metrics.annual_return():.2%}")
print(f"Sharpe Ratio: {report.metrics.sharpe_ratio():.2f}")
print(f"Max Drawdown: {report.metrics.max_drawdown():.2%}")

# Option B: Using get_stats() dictionary (note: different key names!)
stats = report.get_stats()
print(f"CAGR: {stats['cagr']:.2%}")           # 'cagr' not 'annual_return'
print(f"Sharpe: {stats['monthly_sharpe']:.2f}") # 'monthly_sharpe' not 'sharpe_ratio'
print(f"MDD: {stats['max_drawdown']:.2%}")     # same name

# Benchmark comparison (finlab >= 2.0.17): same ffn keys, computed on the
# market benchmark over the backtest period — no need to recompute from
# market.get_benchmark()
bench = report.get_benchmark_stats()
print(f"Benchmark CAGR: {bench['cagr']:.2%} | MDD: {bench['max_drawdown']:.2%}")
```

See [backtesting-reference.md](backtesting-reference.md) for complete `sim()` API.

### Step 4.5: Deliver the FinLab HTML Report (REQUIRED)

Follow each backtest the user will review with one HTML file — the one FinLab generates:

```python
report = sim(position, resample="M", upload=False)
report.to_html("report.html")            # the FinLab-generated file is the deliverable
```

The canonical deliverable is the file generated by `report.to_html()` — do not hand-roll a separate report (custom HTML pages, Plotly summaries, dashboards, markdown files) unless the user explicitly asks. To summarize results, print a short terminal summary and point to the FinLab report. Exception: in batch runs (parameter sweeps, screening many variants), skip per-run HTML and write it only for the final strategy the user will review.

Pick a descriptive filename when running more than one strategy in the same session (e.g. `momentum_top10.html`, `value_lowpb.html`) so the user can compare without overwriting. After writing, tell the user the path so they can open it. Use `report.to_terminal()` only as a supplement for non-GUI terminals; it does not replace the HTML.

See the "`report.to_html()` — the canonical deliverable" section of [backtesting-reference.md](backtesting-reference.md) for details on what the file contains.

### Step 5: Execute Orders (Optional)

Convert backtest results to live trading:

```python
from finlab.online.order_executor import Position, OrderExecutor
from finlab.online.sinopac_account import SinopacAccount

# 1. Convert report to position
position = Position.from_report(report, fund=1000000)

# 2. Connect broker account
acc = SinopacAccount()

# 3. Create executor and preview orders
executor = OrderExecutor(position, account=acc)
executor.create_orders(view_only=True)  # Preview first

# 4. Execute orders (when ready)
executor.create_orders()
```

See [trading-reference.md](trading-reference.md) for complete broker setup and OrderExecutor API.

## Reference Files

| File                                                           | Content                                    |
| -------------------------------------------------------------- | ------------------------------------------ |
| [backtesting-reference.md](backtesting-reference.md)           | `sim()` 參數、stop-loss、rebalancing       |
| [trading-reference.md](trading-reference.md)                   | 券商設定、OrderExecutor、Position          |
| [factor-examples.md](factor-examples.md)                       | 60+ 策略範例                               |
| [dataframe-reference.md](dataframe-reference.md)               | FinLabDataFrame 方法                       |
| [factor-analysis-reference.md](factor-analysis-reference.md)   | IC、Shapley、因子分析                      |
| [best-practices.md](best-practices.md)                         | 常見錯誤、lookahead bias                   |
| [machine-learning-reference.md](machine-learning-reference.md) | ML 特徵工程                                |
| [us-market.md](us-market.md)                                   | US market specifics: data map, quarterly alignment, defaults, universe construction |

## What's New (since v1.5.8)

Short version pointers for features added in recent releases. Each reference file tags the exact API with `(vX.Y.Z)`.

**v2.0.15** (2026-07-18)
- `df.sector(by=...)`: sector accessor now accepts a custom classification — dict / `pd.Series` (stock_id → group) or a time-varying `pd.DataFrame`; unlisted stocks are excluded. Works with all `sector.*` methods — see [dataframe-reference.md](dataframe-reference.md)
- `df.sector.map(mapping)`: broadcast group-level scalars (e.g. sector weights) to full DataFrame shape for factor composition — see [dataframe-reference.md](dataframe-reference.md)
- `df.weight.by_group(weights, by, default)`: allocate capital across sectors/groups — normalize holdings so each group's total equals its share; under-allocation stays in cash — see [dataframe-reference.md](dataframe-reference.md)

**v2.0.12** (2026-06-01)
- `sim()` / `hold_until()`: `trail_stop_activation` — require a minimum unrealized gain before `trail_stop` arms. See [backtesting-reference.md](backtesting-reference.md) and [dataframe-reference.md](dataframe-reference.md)
- `report.to_html(path, title=...)`: standalone HTML now sets browser-tab title + FinLab favicon; pass `title` to disambiguate multi-strategy report folders — see [backtesting-reference.md](backtesting-reference.md)
- Dashboard settings modal: language / light-dark theme / candle color scheme (default, east-red, west-green) consolidated into one panel

**v2.0.9** (2026-05-27)
- `data.set_market("rotc")`: 興櫃 is now a first-class market code; `price:收盤價` / `monthly_revenue:*` / etc. resolve to the `rotc_` catalog and `sim()` uses `ROTCMarket` defaults
- `data.search(market="rotc")`: scoped to the emerging-market catalog only

**v2.0.1** (2026-04-26)
- `python -m finlab cloud` *(CLI)*: deploy strategies to the `finlab-auto-update` Cloud Functions runtime with daily Asia/Taipei scheduling — `deploy`, `get`, `list`, `run`, `logs`, `schedule set/delete`, `delete`, `status`. See [trading-reference.md](trading-reference.md#cloud-strategy-deployment--python--m-finlab-cloud-v201)
- `sim()` peak RSS ~800 MB lower on full-market monthly strategies (was ~2.0–2.2 GiB → ~1.29 GiB); enables s-tier cloud workers that previously OOM'd

**v2.0.0** (2026-04-04) — major release
- `finlab.exceptions`: structured error hierarchy (`FinlabError`, `DataError`, `BacktestError`, ...) — see [backtesting-reference.md](backtesting-reference.md)
- `data.get(lazy=True)` / `data.gets(..., lazy=True)`: batch fetch + deferred compute; `data.override()` / `DataContext` for scoped global state
- `df.cs` / `df.sector` / `df.weight` accessors; `rolling().std/var/skew/kurt/median` — see [dataframe-reference.md](dataframe-reference.md)
- `PositionStreamMixin` for realtime position streaming — see [trading-reference.md](trading-reference.md)
- `from finlab import FinlabDataFrame` top-level export
- `backtest.sim()` refactored into 5 testable stages; `eval()` removed from `optimize.combinations`

**v1.5.13** (2026-03-22)
- `universe(index=...)` / `us_universe(index=...)`: filter US stocks by S&P 500 / NASDAQ 100
- New market code `TW_CB` (TW convertible bonds)

**v1.5.11** (2026-03-11)
- `data.get_role()` / `data.is_vip()`: query user quota tier
- Report migration to canonical Firestore flow (transparent to users)

**v1.5.9**
- `finlab.schemas`: typed `PositionEntry`, `OrderEntry`, `PortfolioData` contracts
- `OrderExecutor.generate_orders(as_entries, quantity_type)` and `generate_order_entries()`
- `PortfolioSyncManager.get_data_typed()` / `set_data_typed()`
- `data.get()` 80% quota usage warning
- `sim()` uses market-specific default `fee_ratio` / `tax_ratio` (no longer hardcoded TW values)

**v1.5.8** (baseline)
- `verify_strategy()`: automated lookahead-bias detector
- `report.to_terminal()`: ASCII report for non-Jupyter runs
- Overall strategy execution 3.4x faster

## Financial Data Alignment

Never use `reindex()` or `reindex_like()`, including on final positions. FinLabDataFrame automatically reshapes dates and stock columns during arithmetic, comparisons and boolean operations: `sales_to_price = eps_sales / close`. Do not manually align or bypass this behavior with pandas/NumPy. Calculate quarterly shifts and rolling windows before combining with daily data; set rebalance schedules with `sim(position, resample=...)`. Use `index_str_to_date()` only to inspect dates. On errors, inspect types and consult [dataframe-reference.md](dataframe-reference.md).

## Prevent Lookahead Bias

**Critical:** Avoid using future data to make past decisions:

```python
# ✅ GOOD: Use shift(1) to get previous value
prev_close = close.shift(1)

# ❌ BAD: Don't use iloc[-2] (can cause lookahead)
# prev_close = close.iloc[-2]  # WRONG

# ✅ GOOD: Leave index as-is even with strings like "2025Q1"
# FinLabDataFrame operators align dates and stock columns automatically

# ❌ BAD: Don't manually assign to df.index
# df.index = new_index  # FORBIDDEN
```

See [best-practices.md](best-practices.md) for more anti-patterns.

## Performance Defaults

**Pass `lazy=True` by default; drop to eager pandas only when debugging.** `data.get(..., lazy=True)` and `data.gets(..., lazy=True)` *(v2.0.0)* return lazy FinlabDataFrames that defer the compute graph until a terminal call materializes it — chained ops avoid redundant passes (single-CPU). Omit `lazy=True` when you need to print/inspect intermediate values interactively.

```python
# ✅ Default: fetch lazy directly
price, volume, pe = data.gets(
    'price:收盤價', 'price:成交股數', 'price_earning_ratio:本益比',
    lazy=True,
)

# ✅ Debug: eager pandas for row-level inspection
close = data.get('price:收盤價')
print(close.loc['2024-01-15', '2330'])
```

## Feedback

Direct users to open an issue on GitHub: https://github.com/koreal6803/finlab-ai/issues

## Notes

- Some data columns use Chinese names — this is expected, use them as-is in `data.get()` calls
- Data frequency varies: daily (price), monthly (revenue), quarterly (financial statements)
- `sim()` defaults to `upload=None`: local runs do not upload; FinLab Studio / cloud schedules (which set `FINLAB_STRATEGY_NAME` / `FINLAB_FORCED_STRATEGY_NAME`) do. Pass `upload=False` to guarantee no upload, `upload=True` to force one
