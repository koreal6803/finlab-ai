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
    fee_ratio: float = 1.425/1000,
    tax_ratio: float = 3/1000,
    name: str = '未命名',
    stop_loss: Union[float, None] = None,
    take_profit: Union[float, None] = None,
    trail_stop: Union[float, None] = None,
    touched_exit: bool = False,
    retain_cost_when_rebalance: bool = False,
    stop_trading_next_period: bool = True,
    live_performance_start: Union[str, None] = None,
    mae_mfe_window: int = 0,
    mae_mfe_window_step: int = 1,
    market: Union[None, Market] = None,
    upload: bool = True,
    fast_mode: bool = False,
    notification_enable: bool = False,
    line_access_token: str = ''
) -> report.Report
```

### Parameters

#### position
- **Type:** `Union[pd.DataFrame, pd.Series]`
- **Required:** Yes
- **Description:** A pandas DataFrame or Series representing the buy/sell signals (True indicates holding, False indicates no position). For short positions, negative values can be used. The index should be a DatetimeIndex, and the columns should represent stock IDs.

#### resample
- **Type:** `Union[str, None]`
- **Default:** `None`
- **Description:** Trading frequency or rebalancing dates specification. It can be a string (e.g., 'D', 'W', 'M'), a DataFrame, Series, or None. When None, rebalancing only occurs on changes in the position.

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
- **Type:** `float`
- **Default:** `1.425/1000`
- **Description:** Commission fee ratio applied during trades.

#### tax_ratio
- **Type:** `float`
- **Default:** `3/1000`
- **Description:** Transaction tax ratio applied when selling stocks.

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
- **Type:** `bool`
- **Default:** `True`
- **Description:** Determines whether to upload the strategy performance report after simulation.

### Returns

An instance of `Report` containing performance metrics, trades, and additional analyses.

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
print(report)
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

# Display metrics
print(report.get_metrics())
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
- Prevent using reindex to align FinlabDataFrame as it already has aligned indices and columns
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
- `report.display`
- `report.get_metrics`

**Important Notes:**
- Use the `sim` function to simulate performance based on your position DataFrame
- If monthly revenue is used (as variable `rev`), please set `resample` to `rev.index`
- If user not mention, please set `resample` to 'ME' or 'Q' to avoid overtrading
- Use `print(report.get_metrics())` to extract performance metrics
- If scoping tradable universe at simulation time, you may wrap the backtest call with `with data.universe(...)` — but NEVER wrap factor/position calculations inside that context

**Example:**
```python
from finlab import backtest

# Simple backtest
report = backtest.sim(position, resample='M')

# Backtest with universe filtering
with data.universe(market='TSE_OTC', exclude_category='金融'):
    report = backtest.sim(position, resample='Q')

# Display metrics
print(report.get_metrics())
report.display()
```

---

## Related References

- [FinlabDataFrame Reference](dataframe-reference.md) - Learn about enhanced DataFrame methods
- [Data Reference](data-reference.md) - Explore available data sources
- [Factor Examples](factor-examples.md) - See complete strategy examples
- [Factor Analysis Reference](factor-analysis-reference.md) - Analyze factor performance
