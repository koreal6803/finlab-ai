# FinlabDataFrame Reference

## Overview

FinlabDataFrame is a powerful extension of pandas DataFrame specifically designed for financial data analysis and backtesting. It provides enhanced functionality for trading strategy development, including automatic index/column alignment, moving averages, entry/exit signal detection, and industry-based ranking.

## Key Features

- Automatic re-alignment of indices and columns during arithmetic and logical operations
- Built-in methods for moving averages and technical calculations
- Entry/exit signal detection for trading strategies
- Industry-based grouping and ranking
- Multi-factor and industry neutralization
- Integration with backtesting workflows

**Contents:** [Constructor](#constructor) | [Index Conversion](#index-conversion-methods) | [Moving Average & Comparison](#moving-average--comparison-methods) | [Selection](#selection-methods) | [Signal Detection](#signal-detection-methods) | [Industry & Category](#industry--category-methods) | [Neutralization](#neutralization-methods) | [Quantile](#quantile-methods) | [Auto Alignment](#automatic-index-alignment) | [Method Chaining](#method-chaining-patterns)

---

## Constructor

### FinlabDataFrame

Converts a regular pandas DataFrame to a FinlabDataFrame with enhanced financial data processing capabilities.

**Signature:**
```python
FinlabDataFrame(df: pd.DataFrame)
```

**Parameters:**
- `df` (pd.DataFrame, required): A pandas DataFrame to be converted to FinlabDataFrame

**Returns:**
- An instance of FinlabDataFrame with enhanced financial data processing capabilities

**Example:**
```python
from finlab.dataframe import FinlabDataFrame
from finlab import data
import pandas as pd

# Convert existing pandas DataFrame to FinlabDataFrame
regular_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
df = FinlabDataFrame(regular_df)

# FinlabDataFrame is also automatically returned by data.get()
price_df = data.get('price:收盤價')  # Returns a FinlabDataFrame
```

---

## Index Conversion Methods

### index_str_to_date

Converts string-formatted financial report indices (e.g., "2022-Q1", "2022-M01") to datetime format based on actual disclosure dates. Essential for aligning financial data with daily price data.

**Signature:**
```python
index_str_to_date() -> FinlabDataFrame
```

**Returns:**
- FinlabDataFrame with datetime index based on actual disclosure dates

**Example:**
```python
from finlab import data

# Financial statement data has string index like "2022-Q1"
cash = data.get('financial_statement:現金及約當現金')
print(cash.index[:3])  # ['2013-Q1', '2013-Q2', '2013-Q3']

# Convert to actual disclosure dates
cash_dated = cash.index_str_to_date()
print(cash_dated.index[:3])  # DatetimeIndex(['2013-05-15', '2013-08-14', ...])
```

**Note:** This method uses actual financial statement disclosure dates from `etl:financial_statements_disclosure_dates`, not simple quarter-end dates.

---

### deadline

Converts financial report indices to regulatory deadline dates (公告截止日). Unlike `index_str_to_date()` which uses actual disclosure dates, this uses the official filing deadlines.

**Signature:**
```python
deadline() -> FinlabDataFrame
```

**Returns:**
- FinlabDataFrame with datetime index based on regulatory filing deadlines

**Example:**
```python
from finlab import data

# Convert quarterly data to deadline dates
cash = data.get('financial_statement:現金及約當現金')
cash_deadline = cash.deadline()

# Convert monthly revenue to deadline dates
revenue = data.get('monthly_revenue:當月營收')
revenue_deadline = revenue.deadline()
```

**Use Case:** Use `deadline()` when you want conservative signal timing that assumes data arrives at the latest possible date. Use `index_str_to_date()` when you want signal timing based on actual historical disclosure.

---

## Moving Average & Comparison Methods

### average

Calculates a moving average over n periods. Returns NaN if more than half the values in the window are NaN.

**Signature:**
```python
average(n: int) -> FinlabDataFrame
```

**Parameters:**
- `n` (int, required): Number of periods for the moving average

**Returns:**
- FinlabDataFrame representing the moving average

**Example:**
```python
from finlab import data

close = data.get('price:收盤價')
sma10 = close.average(10)
sma60 = close.average(60)

# Stock price above moving average
cond = close > sma60
```

---

### rise

Determines if values are rising compared to n periods before. Returns True if current value > value n periods ago.

**Signature:**
```python
rise(n: int = 1) -> FinlabDataFrame
```

**Parameters:**
- `n` (int, optional, default=1): Number of periods to compare

**Returns:**
- Boolean FinlabDataFrame indicating rising trends

**Example:**
```python
from finlab import data

close = data.get('price:收盤價')

# Price higher than 10 days ago
rising = close.rise(10)

# Consecutive rising days
consecutive_rise = close.rise().sustain(3)
```

---

### fall

Determines if values are falling compared to n periods before. Returns True if current value < value n periods ago.

**Signature:**
```python
fall(n: int = 1) -> FinlabDataFrame
```

**Parameters:**
- `n` (int, optional, default=1): Number of periods to compare

**Returns:**
- Boolean FinlabDataFrame indicating falling trends

**Example:**
```python
from finlab import data

close = data.get('price:收盤價')

# Price lower than 10 days ago
falling = close.fall(10)

# Avoid stocks in downtrend
avoid = close.fall(20)
```

---

### sustain

Checks whether a condition is sustained over a moving window of n days. Returns True if the sum of True values in the window meets or exceeds the threshold.

**Signature:**
```python
sustain(nwindow: int, nsatisfy: int = None) -> FinlabDataFrame
```

**Parameters:**
- `nwindow` (int, required): Window length (in days)
- `nsatisfy` (int, optional): Minimum number of True values required; defaults to `nwindow` if not provided

**Returns:**
- Boolean FinlabDataFrame

**Example:**
```python
from finlab import data

close = data.get('price:收盤價')

# Price rising for 3 consecutive days
rising_3days = close.rise().sustain(3)

# Price rising at least 4 out of 5 days
rising_4of5 = close.rise().sustain(5, 4)
```

---

## Selection Methods

### is_largest

Returns a boolean DataFrame where True values represent the top n largest values for each date. Eliminates the need for row-by-row iteration with nlargest.

**Signature:**
```python
is_largest(n: int) -> FinlabDataFrame
```

**Parameters:**
- `n` (int, required): Number of top values to select on each date

**Returns:**
- Boolean FinlabDataFrame with True for top n stocks on each date

**Example:**
```python
from finlab import data
from finlab.backtest import sim

# Select 10 stocks with highest ROA
roa = data.get('fundamental_features:ROA稅後息前')
top_roa = roa.is_largest(10)

# Backtest holding top ROA stocks
report = sim(top_roa, resample='Q')
```

---

### is_smallest

Returns a boolean DataFrame where True values represent the n smallest values for each date.

**Signature:**
```python
is_smallest(n: int) -> FinlabDataFrame
```

**Parameters:**
- `n` (int, required): Number of smallest values to select on each date

**Returns:**
- Boolean FinlabDataFrame with True for bottom n stocks on each date

**Example:**
```python
from finlab import data
from finlab.backtest import sim

# Select 10 stocks with lowest P/B ratio
pb = data.get('price_earning_ratio:股價淨值比')
lowest_pb = pb.is_smallest(10)

# Backtest value strategy
report = sim(lowest_pb, resample='M')
```

---

### rank

Computes ranking across rows or columns. **Includes lookahead bias warning when ranking along the time axis.**

**Signature:**
```python
rank(*args, **kwargs) -> FinlabDataFrame
```

**Parameters:**
- Same parameters as `pandas.DataFrame.rank()`
- `axis` (int or str, default=0): Axis to rank along. **Warning: axis=0 may cause lookahead bias**

**Returns:**
- FinlabDataFrame with rankings

**Example:**
```python
from finlab import data

pb = data.get('price_earning_ratio:股價淨值比')

# SAFE: Cross-sectional ranking (rank stocks against each other per day)
pb_rank = pb.rank(axis=1, pct=True)

# Select stocks in bottom 30% of P/B each day
cheap = pb_rank < 0.3

# WARNING: Time-series ranking triggers LookaheadWarning
# This ranks each stock's current value against its future values
# pb.rank(axis=0)  # Will emit warning - use rolling().rank() instead
```

**Warning:** Ranking along `axis=0` (time axis) uses future data and will emit a `LookaheadWarning`. Use `rolling().rank()` or `expanding().rank()` for safe time-series ranking.

---

## Signal Detection Methods

### is_entry

Identifies entry signal points where the condition switches from False to True.

**Signature:**
```python
is_entry() -> FinlabDataFrame
```

**Returns:**
- Boolean FinlabDataFrame indicating entry signals

**Example:**
```python
from finlab import data

close = data.get('price:收盤價')

# Condition: price in top 10
position = close.is_largest(10)

# Find days when stock enters top 10
entry_signals = position.is_entry()
```

---

### is_exit

Identifies exit signal points where the condition switches from True to False.

**Signature:**
```python
is_exit() -> FinlabDataFrame
```

**Returns:**
- Boolean FinlabDataFrame indicating exit signals

**Example:**
```python
from finlab import data

close = data.get('price:收盤價')

# Condition: price in top 10
position = close.is_largest(10)

# Find days when stock exits top 10
exit_signals = position.is_exit()
```

---

### exit_when

Creates a position DataFrame that enters on entry signals and exits when either the original condition becomes False OR the specified exit condition becomes True.

**Signature:**
```python
exit_when(exit: pd.DataFrame) -> FinlabDataFrame
```

**Parameters:**
- `exit` (pd.DataFrame, required): Additional exit condition DataFrame

**Returns:**
- Boolean FinlabDataFrame representing positions

**Example:**
```python
from finlab import data

close = data.get('price:收盤價')
volume = data.get('price:成交股數')

# Entry: price breaks above 20-day high
entry_cond = close > close.rolling(20).max().shift()

# Additional exit: volume spike (possible distribution)
volume_spike = volume > volume.average(20) * 3

# Position with additional exit condition
position = entry_cond.exit_when(volume_spike)
```

---

### hold_until

Generates trading positions based on entry signals until exit signals occur. Supports stock rotation limits, stop-loss/take-profit, and ranking-based selection.

**Signature:**
```python
hold_until(
    exit: pd.DataFrame,
    nstocks_limit: int = None,
    stop_loss: float = -np.inf,
    take_profit: float = np.inf,
    trade_at: str = 'close',
    rank: pd.DataFrame = None
) -> FinlabDataFrame
```

**Parameters:**
- `exit` (pd.DataFrame, required): Exit signal DataFrame
- `nstocks_limit` (int, optional): Maximum number of stocks to hold simultaneously
- `stop_loss` (float, optional, default=-np.inf): Stop loss threshold (e.g., 0.1 = exit if down 10%)
- `take_profit` (float, optional, default=np.inf): Take profit threshold (e.g., 0.2 = exit if up 20%)
- `trade_at` (str, optional, default='close'): Price reference for stop/take profit ('close' or 'open')
- `rank` (pd.DataFrame, optional): Ranking DataFrame for prioritizing entries when limit is reached (higher = priority)

**Returns:**
- Boolean FinlabDataFrame with positions (True indicates holding)

**Example:**
```python
from finlab import data
from finlab.backtest import sim

close = data.get('price:收盤價')
pb = data.get('price_earning_ratio:股價淨值比')

# Entry: price above 20-day MA
entries = close > close.average(20)

# Exit: price below 60-day MA
exits = close < close.average(60)

# Hold max 10 stocks, prefer lower P/B (use negative for ascending)
position = entries.hold_until(
    exits,
    nstocks_limit=10,
    stop_loss=0.1,      # 10% stop loss
    take_profit=0.3,    # 30% take profit
    rank=-pb            # Lower P/B = higher priority
)

report = sim(position)
```

---

## Industry & Category Methods

### groupby_category

Groups DataFrame columns by their industry category. Similar to `pandas.DataFrame.groupby()` but groups stocks by industry.

**Signature:**
```python
groupby_category() -> pd.core.groupby.DataFrameGroupBy
```

**Returns:**
- A GroupBy object with groups defined by industry categories

**Example:**
```python
from finlab import data

pb = data.get('price_earning_ratio:股價淨值比')

# Average P/B by industry
industry_pb = pb.groupby_category().mean()

# Plot semiconductor industry P/B over time
industry_pb['半導體'].plot(title='Semiconductor P/B Ratio')
```

---

### industry_rank

Calculates percentile ranking for stocks within their respective industries. Returns values from 0 (lowest in industry) to 1 (highest in industry).

**Signature:**
```python
industry_rank(categories: list = None) -> FinlabDataFrame
```

**Parameters:**
- `categories` (list, optional): List of industry categories to consider. If None, uses all industries from `data.get('security_industry_themes')`

**Returns:**
- FinlabDataFrame with industry-relative ranking scores (0 to 1)

**Example:**
```python
from finlab import data

pe = data.get('price_earning_ratio:本益比')

# Rank P/E within each industry
pe_industry_rank = pe.industry_rank()

# Select stocks that are cheap relative to their industry
cheap_in_industry = pe_industry_rank < 0.3
```

---

### entry_price

Retrieves the adjusted price at entry signal points.

**Signature:**
```python
entry_price(trade_at: str = 'close') -> FinlabDataFrame
```

**Parameters:**
- `trade_at` (str, optional, default='close'): Price type ('close' or 'open')

**Returns:**
- FinlabDataFrame with entry prices (forward-filled)

**Example:**
```python
from finlab import data

close = data.get('price:收盤價')

# Position signal
position = close.is_largest(10)

# Get entry prices for calculating returns
entry_prices = position.entry_price()
current_return = close / entry_prices - 1
```

---

## Neutralization Methods

### neutralize

Performs cross-sectional regression to neutralize factors from the data. Returns residuals after regressing on specified neutralizer factors.

**Signature:**
```python
neutralize(
    neutralizers: Union[pd.DataFrame, list[pd.DataFrame], dict[str, pd.DataFrame]],
    add_const: bool = True
) -> FinlabDataFrame
```

**Parameters:**
- `neutralizers` (DataFrame, list, or dict, required): Factor(s) to neutralize against
  - Single DataFrame: neutralize against one factor
  - List of DataFrames: neutralize against multiple factors
  - Dict of DataFrames: neutralize with named factors
- `add_const` (bool, optional, default=True): Whether to include intercept in regression

**Returns:**
- FinlabDataFrame containing regression residuals (neutralized values)

**Example:**
```python
from finlab import data

# Original factor
pe = data.get('price_earning_ratio:本益比')

# Neutralize against size (market cap)
size = data.get('etl:market_value')
pe_size_neutral = pe.neutralize(size)

# Neutralize against multiple factors
pb = data.get('price_earning_ratio:股價淨值比')
pe_multi_neutral = pe.neutralize([size, pb])

# Neutralize with named factors (for clarity)
pe_named_neutral = pe.neutralize({
    'size': size,
    'size_squared': size ** 2,
    'pb': pb
})
```

**Use Case:** Factor neutralization removes unwanted exposures. For example, if you want a value factor that isn't just picking small-cap stocks, neutralize against market cap.

---

### neutralize_industry

Performs cross-sectional regression to neutralize industry effects. Each stock is regressed on industry dummy variables, returning industry-neutral residuals.

**Signature:**
```python
neutralize_industry(
    categories: pd.DataFrame = None,
    add_const: bool = True
) -> FinlabDataFrame
```

**Parameters:**
- `categories` (pd.DataFrame, optional): DataFrame with 'stock_id' and 'category' columns. If None, uses `data.get('security_categories')`
- `add_const` (bool, optional, default=True): Whether to include intercept (one dummy is dropped to avoid multicollinearity)

**Returns:**
- FinlabDataFrame containing industry-neutralized values

**Example:**
```python
from finlab import data

# P/E ratio varies significantly by industry
pe = data.get('price_earning_ratio:本益比')

# Remove industry effects
pe_industry_neutral = pe.neutralize_industry()

# Now pe_industry_neutral represents deviation from industry average
# Positive = expensive relative to industry peers
# Negative = cheap relative to industry peers

# Custom industry categories
custom_cats = pd.DataFrame({
    'stock_id': ['2330', '2317', '1101', '2412'],
    'category': ['半導體', '電子', '水泥', '電信']
})
pe_custom_neutral = pe.neutralize_industry(categories=custom_cats)
```

---

## Quantile Methods

### quantile_row

Computes the specified quantile across all stocks for each date.

**Signature:**
```python
quantile_row(c: float) -> pd.Series
```

**Parameters:**
- `c` (float, required): Quantile value between 0 and 1 (e.g., 0.9 for 90th percentile)

**Returns:**
- pandas Series containing the quantile value per date

**Example:**
```python
from finlab import data

close = data.get('price:收盤價')

# 90th percentile price each day
q90 = close.quantile_row(0.9)

# Median price each day
median = close.quantile_row(0.5)

# Select stocks above 90th percentile
expensive = close > close.quantile_row(0.9)
```

---

## Automatic Index Alignment

FinlabDataFrame automatically aligns indices and columns when performing operations between DataFrames with different frequencies or shapes.

**Supported Operations:**
- Arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Comparison: `>`, `>=`, `==`, `!=`, `<`, `<=`
- Logical: `&`, `|`, `^`

**Example:**
```python
from finlab import data

# Daily data
close = data.get('price:收盤價')  # Daily frequency

# Quarterly data
roa = data.get('fundamental_features:ROA稅後息前')  # Quarterly frequency

# Operations automatically align - no manual reindex needed
cond1 = close > close.average(60)  # Daily condition
cond2 = roa > 0                     # Quarterly condition

# Intersection works across frequencies
# Quarterly data is forward-filled to daily
position = cond1 & cond2
```

**Alignment Rules:**
1. Index: Union of both indices, forward-filled
2. Columns: Intersection of both column sets
3. String indices (e.g., "2022-Q1") are converted to datetime using disclosure dates

---

## Method Chaining Patterns

FinlabDataFrame methods can be chained for concise strategy expression.

**Example: Complete Strategy**
```python
from finlab import data
from finlab.backtest import sim

close = data.get('price:收盤價')
pb = data.get('price_earning_ratio:股價淨值比')
roa = data.get('fundamental_features:ROA稅後息前')

# Chain conditions and selection
position = (
    pb[
        (close > close.average(60)) &     # Above 60-day MA
        (roa > 0) &                        # Profitable
        (close.rise(5))                    # Rising momentum
    ]
    .neutralize_industry()                 # Industry-neutral P/B
    .is_smallest(10)                       # Cheapest 10 stocks
)

report = sim(position, resample='M')
```

---

## Related References

- [Backtesting Reference](backtesting-reference.md) - Learn how to backtest strategies using FinlabDataFrame
- [Data Reference](data-reference.md) - Explore available data sources
- [Factor Examples](factor-examples.md) - See practical examples of using FinlabDataFrame in strategies
- [Best Practices](best-practices.md) - Avoid common pitfalls including lookahead bias
