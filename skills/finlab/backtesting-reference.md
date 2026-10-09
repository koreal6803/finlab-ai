# Backtesting Reference

## Overview

The FinLab backtesting framework allows you to simulate trading strategies using historical data. The `backtest.sim()` function is the core tool for evaluating strategy performance, supporting various parameters for rebalancing, transaction costs, stop-loss/take-profit, and more.

---

## backtest.sim

Simulate the equity curve of a stock portfolio based on its position history and market data. This function supports various parameters for rebalancing frequency, transaction costs, stop loss/take profit, and notification via Line.

**Import:**
```python
from finlab import backtest
```

**Signature:**
```python
sim(
    position: Union[pd.DataFrame, pd.Series],
    resample: Union[str, None] = None,
    resample_offset: Union[str, None] = None,
    trade_at_price: Union[str, pd.DataFrame] = 'close',
    position_limit: float = 1,
    fee_ratio: Union[float, None] = None,   # None -> market default (TW: 1.425/1000)
    tax_ratio: Union[float, None] = None,   # None -> market default (TW: 3/1000)
    name: str = '未命名',
    stop_loss: Union[float, None] = None,
    take_profit: Union[float, None] = None,
    trail_stop: Union[float, None] = None,
    trail_stop_activation: Union[float, None] = None,
    touched_exit: bool = False,
    retain_cost_when_rebalance: bool = False,
    stop_trading_next_period: bool = True,
    live_performance_start: Union[str, None] = None,
    mae_mfe_window: int = 0,
    mae_mfe_window_step: int = 1,
    market: Union[None, Market] = None,
    upload: Union[bool, None] = None,
    *,
    end_date: Union[str, datetime.date, pd.Timestamp, None] = None,
    metrics_only: bool = False,
    notification_enable: bool = False,
    line_access_token: str = ''
) -> Union[report.Report, Metrics]   # Metrics when metrics_only=True
```

### Parameters

#### position
- **Type:** `Union[pd.DataFrame, pd.Series]`
- **Required:** Yes
- **Description:** A pandas DataFrame or Series representing the buy/sell signals (True indicates holding, False indicates no position). For short positions, negative values can be used. The index should be a DatetimeIndex, and the columns should represent stock IDs.

#### resample
- **Type:** `Union[str, None]`
- **Default:** `None`
- **Description:** Trading frequency or rebalancing dates specification. It can be a string (e.g., 'D', 'W', 'M'), a DataFrame, Series, or None. When None, rebalancing only occurs on dates where the position changes (it does not rebalance daily).

#### resample_offset
- **Type:** `Union[str, None]`
- **Default:** `None`
- **Description:** An optional time offset (e.g., '1D', '1H') applied to rebalance dates.

#### trade_at_price
- **Type:** `Union[str, pd.DataFrame]`
- **Default:** `'close'`
- **Description:** Specifies which market price to use in the simulation. Options include 'close', 'open', 'open_close_avg', 'high_low_avg', or a custom DataFrame with price data.

#### position_limit
- **Type:** `float`
- **Default:** `1`
- **Description:** Limit for the maximum weight assigned to any single asset (e.g., 0.2 for 20%).

#### fee_ratio
- **Type:** `Union[float, None]`
- **Default:** `None` → market-specific *(v1.5.9)* — TW: `1.425/1000`, US: resolved from the active `Market` subclass
- **Description:** Commission fee ratio applied during trades. When not explicitly provided, `sim()` consults the target `Market` for its default instead of hardcoding TW-market values, so US/CB backtests use the correct fee schedule automatically.

#### tax_ratio
- **Type:** `Union[float, None]`
- **Default:** `None` → market-specific *(v1.5.9)* — TW: `3/1000`, US: `0`
- **Description:** Transaction tax ratio applied when selling stocks. Resolved from the active `Market` when omitted.

#### name
- **Type:** `str`
- **Default:** `'未命名'`
- **Description:** Name for the strategy (for reporting purposes).

#### stop_loss
- **Type:** `Union[float, None]`
- **Default:** `None`
- **Description:** Stop loss percentage threshold. If set to None, stop loss is disabled.

#### take_profit
- **Type:** `Union[float, None]`
- **Default:** `None`
- **Description:** Take profit percentage threshold. If set to None, take profit is disabled.

#### trail_stop
- **Type:** `Union[float, None]`
- **Default:** `None`
- **Description:** Trailing stop threshold. If set to None, trailing stop is disabled.

#### trail_stop_activation *(v2.0.12)*
- **Type:** `Union[float, None]`
- **Default:** `None`
- **Description:** Unrealized-profit threshold (as a fraction, e.g. `0.05` = +5 %) that a position must reach before `trail_stop` is armed. While the position has not yet hit this gain, the trailing stop is dormant and only the static `stop_loss` (if set) applies. Once the gain is reached, the trail begins watermarking from the running peak as usual. `None` or `0` preserves the pre-2.0.12 behavior of arming `trail_stop` immediately. Works for both long and short positions in `sim()`; on `hold_until()` it controls the long-rotation trailing-take-profit path. Use this to let winners run past entry noise without giving back gains once a real trend forms — e.g. `trail_stop=0.08, trail_stop_activation=0.10` means "do nothing until +10 %, then trail 8 % off the high".

#### touched_exit
- **Type:** `bool`
- **Default:** `False`
- **Description:** Flag to enable price touch exit logic. Use with caution as it may affect candle details.

#### retain_cost_when_rebalance
- **Type:** `bool`
- **Default:** `False`
- **Description:** Whether to carry forward the original cost basis when rebalancing positions.

#### stop_trading_next_period
- **Type:** `bool`
- **Default:** `True`
- **Description:** If a stop loss/take profit event occurs, trading is suspended for the next period.

#### mae_mfe_window
- **Type:** `int`
- **Default:** `0`
- **Description:** Window length for calculating maximum adverse excursion (MAE) and maximum favorable excursion (MFE).

#### mae_mfe_window_step
- **Type:** `int`
- **Default:** `1`
- **Description:** Step interval for the MAE/MFE analysis.

#### upload
- **Type:** `Union[bool, None]`
- **Default:** `None`
- **Description:** Whether to upload the strategy performance report after simulation. With `None` (default), the report is uploaded only when the environment variable `FINLAB_STRATEGY_NAME` or `FINLAB_FORCED_STRATEGY_NAME` is set (FinLab Studio and cloud schedules set them), so a plain local run does not upload. `upload=True` forces an upload; `upload=False` never uploads.

#### end_date *(v2.0.22)*
- **Type:** `Union[str, datetime.date, pd.Timestamp, None]` (keyword-only)
- **Default:** `None`
- **Description:** Inclusive cutoff for positions, prices and the report. A bare date includes the entire day; positions still held at the cutoff remain open in `report.trades`. `None` infers the end from signal spacing.

#### metrics_only
- **Type:** `bool` (keyword-only)
- **Default:** `False`
- **Description:** Return a `Metrics` object (same type as `report.metrics`) without constructing a full `Report`. Faster for parameter sweeps; return-series metrics such as CAGR, Sharpe ratio and max drawdown remain available.

### Returns

An instance of `Report` containing performance metrics, trades, and additional analyses.

---

## Report Class Reference

The `sim()` function returns a `Report` object with multiple APIs for accessing performance metrics.

### Method 1: `report.metrics` (Recommended for single metrics)

Access individual metrics via the `Metrics` instance:

```python
report = sim(position, resample="M", upload=False)

# Individual metric methods
print(f"Annual Return: {report.metrics.annual_return():.2%}")
print(f"Sharpe Ratio: {report.metrics.sharpe_ratio():.2f}")
print(f"Max Drawdown: {report.metrics.max_drawdown():.2%}")
```

### Method 2: `report.get_stats()` (Returns dictionary)

Returns a flat dictionary with all stats. Useful for batch access:

```python
stats = report.get_stats()

# Dictionary keys (note: different names than metrics methods!)
print(f"Annual Return: {stats['cagr']:.2%}")
print(f"Sharpe Ratio: {stats['monthly_sharpe']:.2f}")
print(f"Max Drawdown: {stats['max_drawdown']:.2%}")
print(f"Win Ratio: {stats['win_ratio']:.2%}")
print(f"Total Return: {stats['total_return']:.2%}")
```

**Available keys in `get_stats()`:**
- `cagr` - Compound Annual Growth Rate
- `daily_sharpe` - Daily Sharpe ratio
- `monthly_sharpe` - Monthly Sharpe ratio
- `max_drawdown` - Maximum drawdown (negative value)
- `win_ratio` - Win rate of trades
- `total_return` - Total cumulative return
- `start` - Backtest start date (string)
- `end` - Backtest end date (string)
- `return_table` - Dict of monthly returns by year

### Method 3: `report.get_metrics()` (Structured nested dictionary)

Returns a nested dictionary organized by category:

```python
metrics = report.get_metrics()

# Structured access
print(metrics['profitability']['annualReturn'])
print(metrics['ratio']['sharpeRatio'])
print(metrics['risk']['maxDrawdown'])
```

**Categories:**
- `backtest` - startDate, endDate, feeRatio, taxRatio, market, freq
- `profitability` - annualReturn, alpha, beta, avgNStock, maxNStock
- `risk` - maxDrawdown, avgDrawdown, avgDrawdownDays, valueAtRisk
- `ratio` - sharpeRatio, sortinoRatio, calmarRatio, volatility
- `winrate` - winRate, m12WinRate, expectancy, mae, mfe
- `liquidity` - capacity, disposalStockRatio, warningStockRatio

### `report.to_html()` — the canonical deliverable

**Signature:**
```python
report.to_html(path: str, title: str | None = None) -> None
```

**Parameters:**
- `path` (str, required): output file path; pass a `.html` filename, the file is written in place
- `title` (str, optional, *v2.0.12*): browser-tab title for the exported page. Defaults to the strategy name. Set this when delivering several reports so the user can tell tabs apart at a glance. The FinLab favicon is bundled into the file automatically (also v2.0.12).

**What the file contains:** a single self-contained HTML page (open in any browser, no server) with
- equity curve and benchmark overlay
- drawdown chart and drawdown table
- monthly / annual return heatmap
- full metric panel (CAGR, Sharpe, Sortino, Calmar, MDD, win rate, MAE/MFE, beta/alpha, capacity)
- trade-by-trade table — entry/exit dates, prices, position size, return, holding days

**When to use:** after any `sim()` call the user will review (batch-run exception: see SKILL.md Step 4.5). It is the file the user actually opens to evaluate the strategy. Print-only summaries hide the equity curve and trade list and are not a substitute.

```python
report = sim(position, resample="M", upload=False)
report.to_html("report.html")
# tell the user the path; they open it in a browser
```

For multiple strategies in one session, use descriptive filenames and per-report tab titles so the user can tell them apart without opening the file:
```python
sim(pos_a, name="Momentum").to_html("momentum.html", title="Momentum")
sim(pos_b, name="Value").to_html("value.html", title="Value")
```

### Other Useful Methods

```python
# Display interactive report inside Jupyter / IPython only
report.display()

# Get trade details as a DataFrame (same data the HTML embeds)
trades_df = report.get_trades()

# Persist the full Report object (for later re-rendering / programmatic access)
report.to_pickle("report.pkl")
loaded_report = Report.from_pickle("report.pkl")

# Run specific analysis modules (also rendered into to_html output)
report.run_analysis("Drawdown")
report.run_analysis("MaeMfe")

# ASCII fallback for terminals without a browser — supplement, not replacement
report.to_terminal()
report.to_terminal(height=8, width=60, show_benchmark=False)
```

### Key Attribute Mappings

| Desired Metric | `report.metrics.X()` | `report.get_stats()['X']` |
|----------------|----------------------|---------------------------|
| Annual Return | `annual_return()` | `'cagr'` |
| Sharpe Ratio | `sharpe_ratio()` | `'monthly_sharpe'` |
| Max Drawdown | `max_drawdown()` | `'max_drawdown'` |
| Win Rate | `win_rate()` | `'win_ratio'` |
| Total Return | - | `'total_return'` |

---

## Example Usage

### Basic Example

```python
import pandas as pd
from finlab import backtest

# Example position DataFrame with dates as index
position = pd.DataFrame({
    '2330': [0, 1, 1],
    '1101': [0.2, 0, 0],
    '2454': [0.4, 0, 0]
}, index=pd.to_datetime(['2021-12-31', '2022-03-31', '2022-06-30']))

report = backtest.sim(position)
report.to_html("report.html")
```

### Advanced Example with Stop Loss and Take Profit

```python
from finlab import data, backtest

close = data.get('price:收盤價')
pb = data.get('price_earning_ratio:股價淨值比')

# Define entry and exit conditions
entries = close > close.average(20)
exits = close < close.average(60)

# Create position with ranking
position = entries.hold_until(exits, nstocks_limit=10, rank=-pb)

# Backtest with stop loss and take profit
report = backtest.sim(
    position,
    resample='M',
    stop_loss=0.1,      # 10% stop loss
    take_profit=0.2,    # 20% take profit
    name='MA Strategy with SL/TP'
)

# Display metrics + write the report
print(report.get_metrics())
report.to_html("ma_strategy.html")
```

---

## Strategy Development Workflow

### Step 1: Fetching Data

Gather the necessary data using `data.get()`, including historical prices, volume, and any relevant indicators.

**Important Notes:**
- Use `with data.universe(...)` ONLY to scope `data.get(...)` calls; do NOT wrap position DataFrame operations
- When specifying category/exclude_category, use industry names only (no numeric codes like '28')

**Example:**
```python
from finlab import data

close = data.get('price:收盤價')
volume = data.get('price:成交股數')
revenue = data.get('monthly_revenue:當月營收')
```

---

### Step 2: Factor Creation

Create factors or indicators that will be used in your strategy.

**Available Methods:**
- `average`, `rolling(n).mean`, `rolling(n).std`, `rolling(n).max`, `rolling(n).min`
- `is_largest`, `is_smallest`
- `sustain`, `rise`, `fall`
- `industry_rank`, `quantile_row`
- Arithmetic operators: `+`, `-`, `*`, `/`
- Comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Logical operators: `&`, `|`, `~`

**Important Notes:**
- Do not use `==` for floating point comparisons. Use `np.isclose()` instead
- Be cautious with `&` and `|` operators; ensure proper parentheses to avoid precedence issues
- Never use `reindex()` or `reindex_like()`, including on final positions; use `sim(position, resample=...)` for schedules. FinlabDataFrame arithmetic, comparisons and boolean indexing automatically align dates and stock columns, including quarterly financial statements versus daily prices. For example, use `sales_to_price = eps_sales / close` directly.
- Do not use for loops to iterate over rows or columns. Use vectorized operations instead

**Example:**
```python
# Calculate moving averages
sma20 = close.average(20)
sma60 = close.average(60)

# Revenue growth
rev_growth = revenue.pct_change(12)

# Combine multiple conditions
strong_momentum = (close > sma20) & (close > sma60)
```

---

### Step 3: Construct Position

Define the DataFrame structure for your trading positions. The index should be a DatetimeIndex, and the columns should represent stock IDs. Use boolean values to indicate whether to hold or not, or numeric values for position sizes.

**Important Notes:**
- If user does not mention the sell condition, you can just use `position = a & b & c`
- Without sell condition, the position will be held until the end of the resample period, which is recommended, since we can set stop loss or take profit in the sim function
- If user mentions the sell condition, it is recommended to use `position = buy.hold_until(sell)` where buy is `(a & b & c)` and sell is `(a | b | c)`
- Use `&` and `|` to combine multiple conditions, and use parentheses to ensure correct precedence
- DO NOT use for loop to iterate over rows or columns. FinlabDataFrame already has aligned indices and columns for you

**Example:**
```python
# Simple position without explicit sell condition
position = (close > sma20) & (rev_growth > 0.1)

# Position with entry and exit signals
buy = (close > sma20) & (volume > volume.average(20))
sell = (close < sma60) | (rev_growth < 0)
position = buy.hold_until(sell, nstocks_limit=10)
```

---

### Step 4: Backtest the Strategy

Test your strategy's performance and make adjustments as needed.

**Associated Methods:**
- `backtest.sim`
- `report.to_html` — write the FinLab HTML report (emit for any backtest the user will review)
- `report.get_metrics`
- `report.display` (Jupyter only)

**Important Notes:**
- Use the `sim` function to simulate performance based on your position DataFrame
- If monthly revenue is used (as variable `rev`), please set `resample` to `rev.index`
- If user not mention, please set `resample` to 'ME' or 'Q' to avoid overtrading
- Use `print(report.get_metrics())` to extract performance metrics
- **Call `report.to_html("report.html")` for any backtest the user will review** so they have a browsable report with equity curve, drawdown, monthly returns, and the trade table. Print-only output is not enough.
- If scoping tradable universe at simulation time, you may wrap the backtest call with `with data.universe(...)` — but NEVER wrap factor/position calculations inside that context

**Example:**
```python
from finlab import backtest

# Simple backtest
report = backtest.sim(position, resample='M')

# Backtest with universe filtering
with data.universe(market='TSE_OTC', exclude_category='金融'):
    report = backtest.sim(position, resample='Q')

# Inspect metrics + write the FinLab HTML report
print(report.get_metrics())
report.to_html("report.html")  # the file is what the user opens
```

---

## Lookahead Bias Self-Check — `verify_strategy()`

*(v1.5.8)* When the user asks to check lookahead bias, `verify_strategy()` runs the full strategy once, then reruns it with data truncated at historical dates (`n_tests=5` by default). It compares trades before each cutoff to detect signals that depend on future data. This diagnostic runs multiple backtests and can be slow.

Pass a zero-argument function that fetches data, builds positions, and returns the `Report` from `sim()` inside the function. Returning only a position DataFrame does not satisfy this contract.

```python
from finlab import data
from finlab.backtest import sim
from finlab.verify import verify_strategy

def my_strategy():
    close = data.get('price:收盤價')
    position = close == close.rolling(20).max()
    return sim(position, resample='M', upload=False)

result = verify_strategy(my_strategy, n_tests=5)
print(result.passed)
print(result.summary_df)
if not result.passed:
    print(result.details)
```

The detector returns a `VerifyResult`; detected lookahead bias sets `result.passed` to `False` rather than raising an exception. Inspect `result.summary_df` and `result.details`, then fix the signal before live trading. See [best-practices.md](best-practices.md#-use-verify_strategy-to-auto-detect-lookahead-bias) for parameters and result fields.

---

## Exception Hierarchy — `finlab.exceptions`

*(v2.0.0)* Previously most errors were raised as bare `Exception` or `ValueError`. Production code can now `except` on specific subclasses:

```python
from finlab.exceptions import (
    FinlabError,      # root — catch-all for finlab-specific errors
    DataError,        # data fetch / parsing / schema
    BacktestError,    # sim() validation and execution
    BrokerError,      # broker account / order submission
    AuthError,        # login / token refresh
    PortfolioError,   # PortfolioSyncManager sync failures
    ConfigError,      # invalid configuration
)

try:
    report = backtest.sim(position, resample='M')
except BacktestError as e:
    logger.warning(f"backtest failed: {e}")
except DataError:
    logger.error("data layer failure — abort run")
```

Internally `sim()` was refactored (v2.0.0) into five independently testable stages — `_validate_sim_inputs`, `_prepare_price_data`, `_normalize_position`, `_execute_simulation`, `_build_sim_report` — so errors now originate from a narrower context, which is why most call sites raise a specific `BacktestError` subclass instead of a generic exception.

---

## Related References

- [FinlabDataFrame Reference](dataframe-reference.md) - Learn about enhanced DataFrame methods
- Use `data.search('keyword')` to explore available data sources (use Traditional Chinese keywords for TW market, English for US market)
- [Factor Examples](factor-examples.md) - See complete strategy examples
- [Factor Analysis Reference](factor-analysis-reference.md) - Analyze factor performance
