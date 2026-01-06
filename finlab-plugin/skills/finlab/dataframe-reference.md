# FinlabDataFrame Reference

## Overview

FinlabDataFrame is a powerful extension of pandas DataFrame specifically designed for financial data analysis and backtesting. It provides enhanced functionality for trading strategy development, including automatic index/column alignment, moving averages, entry/exit signal detection, and industry-based ranking.

## Key Features

- Automatic re-alignment of indices and columns during arithmetic and logical operations
- Built-in methods for moving averages and technical calculations
- Entry/exit signal detection for trading strategies
- Industry-based grouping and ranking
- Integration with backtesting workflows

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
import pandas as pd

# Convert existing pandas DataFrame to FinlabDataFrame
regular_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
df = FinlabDataFrame(regular_df)

# FinlabDataFrame is also automatically returned by data.get()
from finlab import data
price_df = data.get('price:收盤價')  # Returns a FinlabDataFrame
```

---

## Methods

### average

Calculates a moving average over n periods.

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
sma = close.average(10)
```

---

### is_largest

Returns a boolean DataFrame where True values represent the top n largest values for each date. Eliminates the need for row-by-row iteration with nlargest, making stock selection simple and efficient.

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
# Select 10 stocks with highest market value daily
top_market_value = data.get('etl:market_value').is_largest(10)
```

---

### is_smallest

Returns a boolean DataFrame where True values represent the n smallest values for each date. Perfect for stock selection without looping through each date with nsmallest.

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
# Select 10 stocks with lowest PE ratio daily
lowest_pe = data.get('price_earning_ratio:本益比').is_smallest(10)
```

---

### sustain

Checks whether the condition is sustained over a moving window of n days, returning True if the sum meets or exceeds a given threshold.

**Signature:**
```python
sustain(nwindow: int, nsatisfy: int = None) -> FinlabDataFrame
```

**Parameters:**
- `nwindow` (int, required): Window length (in days)
- `nsatisfy` (int, optional): Minimum number of True values required; defaults to nwindow if not provided

**Returns:**
- Boolean FinlabDataFrame

**Example:**
```python
sustained = df.rise().sustain(2)
```

---

### rise

Determines if values are rising compared to n periods before.

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
rising = df.rise(10)
```

---

### fall

Determines if values are falling compared to n periods before.

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
falling = df.fall(10)
```

---

### groupby_category

Groups the DataFrame columns based on their associated industry or category.

**Signature:**
```python
groupby_category() -> pd.core.groupby.generic.DataFrameGroupBy
```

**Returns:**
- A GroupBy object with groups defined by industry categories

**Example:**
```python
grouped = df.groupby_category()
mean_category = grouped.mean()
```

---

### entry_price

Retrieves the adjusted price corresponding to entry signals based on a specified price type.

**Signature:**
```python
entry_price(trade_at: str = 'close') -> FinlabDataFrame
```

**Parameters:**
- `trade_at` (str, optional, default='close'): The price type to reference ('close' or 'open')

**Returns:**
- FinlabDataFrame of entry prices

**Example:**
```python
price = df.entry_price()
```

---

### industry_rank

Calculates ranking scores for stocks within their respective industries, where 0 indicates the lowest and 1 the highest.

**Signature:**
```python
industry_rank(categories: list = None) -> FinlabDataFrame
```

**Parameters:**
- `categories` (list, optional): Optional list of industry categories to consider. If omitted, all industries are used

**Returns:**
- FinlabDataFrame of industry ranking scores

**Example:**
```python
rank_scores = df.industry_rank()
```

---

### is_entry

Identifies entry signal points where the condition switches to True.

**Signature:**
```python
is_entry() -> FinlabDataFrame
```

**Returns:**
- Boolean FinlabDataFrame indicating entry signals

**Example:**
```python
entry_signals = df.is_entry()
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
exit_signals = df.is_exit()
```

---

### quantile_row

Computes the specified quantile for each row in the DataFrame.

**Signature:**
```python
quantile_row(c: float) -> pd.Series
```

**Parameters:**
- `c` (float, required): Quantile value (e.g., 0.9 for 90th percentile)

**Returns:**
- pandas Series containing the quantile value per row

**Example:**
```python
q90 = df.quantile_row(0.9)
```

---

### hold_until

Generates trading positions based on entry signals until exit signals occur. Supports additional criteria such as a maximum number of stocks, stop-loss/take-profit thresholds, and ranking to prioritize entries.

**Signature:**
```python
hold_until(
    exit: FinlabDataFrame,
    nstocks_limit: int = None,
    stop_loss: float = -np.inf,
    take_profit: float = np.inf,
    trade_at: str = 'close',
    rank: FinlabDataFrame = None,
    market: str = 'AUTO'
) -> FinlabDataFrame
```

**Parameters:**
- `exit` (FinlabDataFrame, required): A FinlabDataFrame representing exit signals
- `nstocks_limit` (int, optional): Maximum number of stocks to hold (if None, holds all available)
- `stop_loss` (float, optional, default=-np.inf): Stop loss threshold (default: -np.inf, meaning off)
- `take_profit` (float, optional, default=np.inf): Take profit threshold (default: np.inf, meaning off)
- `trade_at` (str, optional, default='close'): Price reference for evaluating stop loss/take profit ('close' or 'open')
- `rank` (FinlabDataFrame, optional): Optional FinlabDataFrame for ranking stocks when entries exceed the limit
- `market` (str, optional, default='AUTO'): Market identifier; default is 'AUTO'

**Returns:**
- Boolean FinlabDataFrame with positions (True indicates holding a stock)

**Example:**
```python
from finlab import data
close = data.get('price:收盤價')
pb = data.get('price_earning_ratio:股價淨值比')

entries = close > close.average(20)
exits = close < close.average(60)

position = entries.hold_until(exits, nstocks_limit=10, rank=-pb)
```

---

## Related References

- [Backtesting Reference](backtesting-reference.md) - Learn how to backtest strategies using FinlabDataFrame
- [Data Reference](data-reference.md) - Explore available data sources
- [Factor Examples](factor-examples.md) - See practical examples of using FinlabDataFrame in strategies
