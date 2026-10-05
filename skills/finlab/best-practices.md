# FinLab Best Practices and Anti-Patterns

This document contains critical coding patterns, anti-patterns, and best practices for developing FinLab strategies. **Following these guidelines prevents common errors, lookahead bias, and data pollution.**

## Table of Contents

1. [Code Patterns (DO THIS)](#code-patterns-do-this)
2. [Anti-Patterns (DON'T DO THIS)](#anti-patterns-dont-do-this)
3. [Preventing Future Data Pollution](#preventing-future-data-pollution)
4. [Stock Selection Patterns](#stock-selection-patterns)
5. [Backtesting Patterns](#backtesting-patterns)
6. [Error Handling](#error-handling)

---

## Code Patterns (DO THIS)

### ✅ Combine Conditions with Logical Operators

**DO:** Use `&`, `|`, `~` to combine conditions into a single position DataFrame.

```python
from finlab import data
from finlab.backtest import sim

factor1 = data.get("price:收盤價")
factor2 = data.get("monthly_revenue:當月營收")
factor3 = data.get("price_earning_ratio:本益比")

cond1 = factor1.rank(axis=1, pct=True) > 0.5
cond2 = factor2.rank(axis=1, pct=True) > 0.5

cond_intersection = cond1 & cond2
position = factor3[cond_intersection].is_smallest(5)

report = sim(position, resample="M")
```

**DON'T:** Create separate functions to generate positions (adds unnecessary complexity).

### ✅ Use `is_smallest()` or `is_largest()` for Stock Selection

**DO:** Limit to top N < 50 stocks using these methods.

```python
# Select top 10 stocks by lowest P/E
pe = data.get("price_earning_ratio:本益比")
position = pe.is_smallest(10)

# Select top 15 stocks by highest momentum, where condition is met
close = data.get("price:收盤價")
momentum = close / close.shift(20) - 1
condition = close > close.average(60)
position = momentum[condition].is_largest(15)
```

**Note:** The DataFrame used with `is_smallest()`/`is_largest()` must have **float dtype**, not bool. If you have a boolean condition, apply it as a filter first.

### ✅ Use Correct Technical Indicator Syntax

**DO:** Call `data.indicator()` without passing OHLCV data.

```python
# Correct - no OHLCV parameters
rsi = data.indicator("RSI", timeperiod=14)

# Correct - multiple return values
macd, macd_signal, macd_hist = data.indicator(
    "MACD",
    fastperiod=12,
    slowperiod=26,
    signalperiod=9
)

# Correct - Bollinger Bands
upperband, middleband, lowerband = data.indicator(
    "BBANDS",
    timeperiod=20,
    nbdevup=2.0,
    nbdevdn=2.0,
    matype=0
)
```

**DON'T:** Pass close price or OHLCV data to indicators.

```python
# ❌ WRONG - don't pass close
rsi = data.indicator("RSI", close, timeperiod=14)  # ERROR
```

### ✅ Use `df.shift(1)` for Previous Values

**DO:** Use `.shift()` to access historical data.

```python
# Correct - get previous day's close
prev_close = close.shift(1)

# Correct - detect crossover
sma20 = close.average(20)
sma60 = close.average(60)
golden_cross = (sma20 > sma60) & (sma20.shift() < sma60.shift())
```

**DON'T:** Use `.iloc[-2]` or similar indexing (can cause lookahead bias).

```python
# ❌ WRONG
prev_close = close.iloc[-2]  # DON'T USE THIS
```

### ✅ Use `data.universe()` for Filtering

**DO:** Use context manager or `set_universe()` to filter stocks by market/category.

```python
from finlab import data

# Method 1: Context manager (temporary scope)
with data.universe(market='TSE_OTC', category=['水泥工業']):
    price = data.get('price:收盤價')

# Method 2: Set globally
data.set_universe(market='TSE_OTC', category='半導體', exclude_category='金融')
price = data.get('price:收盤價')
```

Use `data.search('keyword', market='<market>')` to discover available datasets and `data.universe()` parameters. Supported markets: `tw`, `us`, `kr`, `jp`, `hk`. Use keywords in the dataset's native language (e.g. `'營收'` for `tw`, `'revenue'` for `us`).

### ✅ Always Write `report.to_html()` After `sim()`

**DO:** Treat the FinLab-generated HTML file as the actual deliverable of a backtest. Numbers in the terminal are not a substitute — the user needs to see the equity curve, drawdown, and the trade table to judge whether the strategy is worth keeping.

```python
report = sim(position, resample="M", upload=False)
report.to_html("report.html")   # equity curve + metrics + trade list, browser-openable
print(f"CAGR {report.get_stats()['cagr']:.2%}  Sharpe {report.get_stats()['monthly_sharpe']:.2f}")
print("Open report.html to inspect the full report.")
```

When running several strategies in one session, name the files so they don't clobber each other (`momentum.html`, `value.html`). See the "`report.to_html()` — the canonical deliverable" section of [backtesting-reference.md](backtesting-reference.md) for what the file contains.

**DON'T:** End the workflow at `print(report.get_metrics())`. The user cannot inspect drawdown periods, return seasonality, or individual losing trades from a metric dump alone.

### ✅ Assign `resample` to Prevent Overtrading

**DO:** Always specify `resample` parameter in `sim()`.

```python
# Monthly rebalancing
sim(position, resample="M")

# Weekly rebalancing
sim(position, resample="W")

# Use monthly revenue index
rev = data.get('monthly_revenue:當月營收')
sim(position, resample=rev.index)
```

**DON'T:** Omit `resample` for ranking/factor strategies. With the default `resample=None`, `sim()` rebalances on every date the position changes, so a daily-updated signal (e.g. daily rank) trades daily and overtrades.

---

## Anti-Patterns (DON'T DO THIS)

### ❌ Don't Use `==` for Float Comparisons

**Reason:** Floating point precision issues.

```python
# ❌ BAD
condition = (close == 100.0)

# ✅ GOOD - use inequalities or np.isclose()
import numpy as np
condition = np.isclose(close, 100.0)
# Or better:
condition = (close > 99.9) & (close < 100.1)
```

### ❌ Don't Manually Align FinLabDataFrame Frequencies

**Reason:** FinLabDataFrame already automatically aligns indices/columns. When monthly or quarterly string-index data is combined with daily data through FinLabDataFrame operators or boolean indexing, internal `reshape()` calls `index_str_to_date()` automatically, then forward-fills on the combined date grid. This applies to both Taiwan data such as `monthly_revenue:*` / `fundamental_features:*` and US data such as `us_income_statement:*` / `us_balance_sheet:*`.

```python
# Automatic PIT alignment
close = data.get("price:收盤價")
roe = data.get("fundamental_features:ROE稅後")
position = (close > close.average(60)) & (roe > 0)
```

The same pattern applies to pure quarterly factors: calculate them on the original string index first, then combine with daily conditions directly.

```python
net_income = data.get("us_income_statement:net_income")
equity = data.get("us_balance_sheet:total_stockholders_equity")
close = data.get("us_price:adj_close")

roe = net_income / equity
position = (roe > 0.15) & (close > 5)  # reshape() handles filing-date alignment
```

Never use `reindex()` or `reindex_like()`, including on final positions. Use `sim(position, resample=...)` for rebalance schedules and `.index_str_to_date()` only to inspect dates.

### ❌ Don't Use For Loops

**Reason:** FinLabDataFrame methods are vectorized and much faster.

```python
# ❌ BAD - iterating over rows
for date in close.index:
    for stock in close.columns:
        if close.loc[date, stock] > sma60.loc[date, stock]:
            position.loc[date, stock] = True

# ✅ GOOD - vectorized operations
position = close > sma60
```

### ❌ Don't Filter 注意股/處置股/全額交割股 Unless Asked

**Reason:** These filters remove many stocks and should only be applied when explicitly requested.

```python
# ❌ DON'T do this by default
is_regular = (
    data.get("etl:noticed_stock_filter") &
    data.get("etl:disposal_stock_filter") &
    data.get("etl:full_cash_delivery_stock_filter")
)
position = position & is_regular

# ✅ Only do this if user specifically asks to remove these stocks
```

### ❌ Don't Pass OHLCV to Technical Indicators

**Reason:** `data.indicator()` automatically uses correct price data.

```python
# ❌ WRONG
close = data.get("price:收盤價")
rsi = data.indicator("RSI", close, timeperiod=14)  # ERROR

# ✅ CORRECT
rsi = data.indicator("RSI", timeperiod=14)  # Automatically uses close
```

### ❌ Don't Use Boolean Indexing with Mismatched Indices

**Reason:** When extracting `.iloc[-1]` from DataFrames with different columns, the resulting Series have different indices. Boolean indexing then fails with `IndexingError`.

```python
# ❌ BAD - indices may not match
selected = latest_pe[latest_combined]  # IndexingError

# ✅ GOOD - align indices first
common = latest_combined.index.intersection(latest_pe.index)
selected = latest_pe.loc[common][latest_combined.loc[common]]
```

---

## Preventing Future Data Pollution

**Critical:** Future data pollution (lookahead bias) occurs when you use information that wouldn't have been available at the time of decision-making. This silently corrupts backtests and makes them unrealistic.

### ✅ Leave `df.index` As-Is

**DO:** Keep index intact, even if it contains strings like "2025Q1".

```python
# ✅ GOOD - leave index as-is
revenue = data.get("monthly_revenue:當月營收")
# Index may contain strings like "2022-01", "2022-02", etc.
# FinLabDataFrame operators align dates and stock columns automatically
position = revenue > revenue.shift(1)
```

**DON'T:** Manually assign to `df.index`.

```python
# ❌ FORBIDDEN - can corrupt shared data
df.index = new_index  # NEVER DO THIS
```

### ✅ Let FinLab Handle Alignment and Rebalancing

Use `sales_to_price = eps_sales / close` directly. Never use `reindex()` or `reindex_like()`, including on final positions. Set schedules through `sim(position, resample="M")` or `sim(position, resample=rev)` for revenue releases. Calculate quarterly `shift(4)` or `rolling(4)` before combining with daily prices. Do not overwrite financial indices, backfill future observations, or bypass alignment through pandas/NumPy. Inspect types and consult the dataframe reference if an operation fails.

### ✅ Use `verify_strategy()` to Auto-Detect Lookahead Bias

`verify_strategy()` automatically tests your strategy for lookahead bias by truncating data at historical dates and comparing results against a full-data run.

> **Note:** This is a diagnostic tool — it runs the full strategy multiple times and is slow. Only use it when the user explicitly asks to verify lookahead bias. Do NOT run it as part of routine strategy building. Requires finlab >= 1.5.8 (`pip install finlab --upgrade`).

```python
from finlab.verify import verify_strategy
from finlab import data
from finlab.backtest import sim

def my_strategy():
    close = data.get('price:收盤價')
    pb = data.get('price_earning_ratio:股價淨值比')
    position = pb[close > close.average(60)].is_smallest(10)
    return sim(position, resample='M', upload=False)

result = verify_strategy(my_strategy, n_tests=5)
print(result.passed)       # True = no bias detected
print(result.summary_df)   # Per-date test results
```

**Parameters:**
- `strategy` (Callable, required): Zero-arg function returning a `Report` (output of `sim()`)
- `n_tests` (int, default=5): Number of random truncation dates to test
- `test_dates` (list[str], optional): Explicit dates (YYYY-MM-DD) to test in addition to random sample
- `verbose` (bool, default=True): Print progress and summary

**Returns:** `VerifyResult` with `.passed`, `.n_tests`, `.n_passed`, `.n_failed`, `.summary_df`, `.details`

---

## Stock Selection Patterns

### Pattern 1: Limit to Top X% of Indicator

```python
# Select stocks in top 30% by momentum
momentum = close / close.shift(60) - 1
top_momentum = momentum.rank(axis=1, pct=True) > 0.7
```

### Pattern 1b: Stable Percentile Ranking with `valid=`

When using `fillna()` before ranking (e.g. to compute indicators like SLOPE), the filled values inflate the rank denominator and shift all percentiles. Use `valid=` to exclude them:

```python
ratio = close / close.shift(5)
# fillna(1) needed for SLOPE, but those cells shouldn't count in rank
score = ratio.fillna(1).apply(lambda s: talib.LINEARREG_SLOPE(s, timeperiod=5))
pct = score.rank(axis=1, pct=True, valid=ratio.notna())
```

### Pattern 2: Limit to Top N Stocks

```python
# Select top 10 stocks with lowest P/B ratio
pb = data.get("price_earning_ratio:股價淨值比")
position = pb.is_smallest(10)

# Select top 15 stocks meeting a condition
volume = data.get("price:成交股數")
liquid_stocks = volume.average(20) > 1000*1000
position = pb[liquid_stocks].is_smallest(15)
```

### Pattern 3: Entry/Exit with `hold_until()`

```python
close = data.get("price:收盤價")
pb = data.get("price_earning_ratio:股價淨值比")

# Define entry and exit signals
entries = close > close.average(20)
exits = close < close.average(60)

# Hold until exit, limit to 10 stocks, rank by negative P/B
position = entries.hold_until(
    exits,
    nstocks_limit=10,
    rank=-pb  # Negative for ascending order (low P/B preferred)
)
```

### Pattern 4: Industry Ranking

```python
# Select top 20% within each industry
roe = data.get("fundamental_features:ROE稅後")
industry_top = roe.industry_rank() > 0.8
```

---

## Backtesting Patterns

### Pattern 1: Basic Backtest

```python
sim(position, resample="M")
```

### Pattern 2: Backtest Within Date Range

Requires FinLab >= 2.0.22. See [end_date](backtesting-reference.md#end_date) for the inclusive cutoff.

```python
sim(position.loc['2020':], resample="M", end_date='2023-12-31')
```

### Pattern 3: Optuna Parameter Optimization

```python
import optuna
from finlab.backtest import sim

def run_strategy(params):
    """Strategy function that returns a report"""
    sma_short = close.average(params['short'])
    sma_long = close.average(params['long'])
    position = (sma_short > sma_long)
    report = sim(position, resample="M", upload=False)
    return report

def objective(trial):
    params = {
        'short': trial.suggest_int('short', 5, 30),
        'long': trial.suggest_int('long', 40, 120)
    }
    report = run_strategy(params)
    return report.metrics.sharpe_ratio()

# Optimize with n_trials <= 10
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=10)
print(f"Best params: {study.best_params}")
```

### Pattern 4: Evaluate Strategy Condition Coverage

```python
# Check how often the condition is True (on average across stocks)
condition = close > close.average(60)
coverage = condition.sum(axis=1).loc['2020':].mean()
print(f"Average stocks meeting condition: {coverage:.1f}")
```

### Pattern 5: Adjust Rebalance Frequency

```python
# Weekly
sim(position, resample="W")

# Monthly
sim(position, resample="M")

# Quarterly
sim(position, resample="Q")

# Custom: use monthly revenue index
rev = data.get('monthly_revenue:當月營收')
sim(position, resample=rev.index)
```

### Pattern 6: Adjust Rebalance Offset

```python
# Rebalance 1 week after period start
sim(position, resample="M", resample_offset="1W")

# Rebalance 1 month after quarter start
sim(position, resample="Q", resample_offset="1M")
```

---

## Error Handling

### Error: `_ArrayMemoryError`

**Solution:** Reset kernel and try again.

```python
# Call this if you encounter _ArrayMemoryError
resetKernel()
```

### Error: `requests.exceptions.ConnectionError`

**Solution:** Reset kernel and retry.

```python
resetKernel()
```

### Error: 用量超限 (Quota Exceeded)

**常見訊息:** `quota exceeded`, `daily limit reached`, `用量已達上限`

**解決方案:**

1. **等待重置** - UTC+8 早上 8 點會自動重置用量
2. **升級方案** - 升級可獲得更多資料用量，詳見 https://www.finlab.finance/payment
3. **減少用量** - 避免重複取得相同數據，將常用數據存入變數；使用 `data.universe()` 限制股票範圍

### Debugging Tips

1. **Break down experiments into small steps**

   ```python
   # Step 1: Fetch data
   close = data.get("price:收盤價")
   print(close.head())

   # Step 2: Create condition
   condition = close > close.average(60)
   print(condition.head())

   # Step 3: Select stocks
   position = condition.is_largest(10)
   print(position.head())
   ```

2. **Inspect variable values** after each step to ensure correctness.

3. **Use print statements** to display intermediate DataFrames.

---

## Strategy Design Principles

### Principle 1: Be Systematic

- **Good:** Clearly define hypothesis, experiment setup, and evaluation criteria
- **Good:** Import optuna to systematically explore parameter space
- **Bad:** Randomly changing parameters without a clear plan

### Principle 2: Start Simple

- Begin with a baseline strategy
- Add complexity incrementally
- Test each addition separately

### Principle 3: Write Clear, Maintainable Code

- Use descriptive variable names
- Add comments where logic isn't self-evident
- Don't over-comment obvious operations

---

## Complete Pattern Examples

### Example 1: Value + Momentum + Liquidity

```python
from finlab import data
from finlab.backtest import sim

# Fetch data
close = data.get("price:收盤價")
pb = data.get("price_earning_ratio:股價淨值比")
volume = data.get("price:成交股數")

# Create factors
value = pb.rank(axis=1, pct=True) < 0.3  # Low P/B
momentum = close.rise(20)  # Rising
liquidity = volume.average(20) > 500*1000  # Liquid

# Combine
position = value & momentum & liquidity
position = pb[position].is_smallest(10)

# Backtest
report = sim(position, resample="M", stop_loss=0.08, upload=False)
report.to_html("value_momentum.html")
print(f"Annual Return: {report.metrics.annual_return():.2%}")
print(f"Sharpe Ratio: {report.metrics.sharpe_ratio():.2f}")
print(f"Max Drawdown: {report.metrics.max_drawdown():.2%}")
```

### Example 2: Monthly Revenue Growth

```python
from finlab import data
from finlab.backtest import sim

# Fetch revenue data
rev = data.get("monthly_revenue:當月營收")
rev_growth = data.get("monthly_revenue:去年同月增減(%)")

# Revenue momentum
rev_ma3 = rev.average(3)
rev_high = (rev_ma3 / rev_ma3.rolling(12).max()) == 1

# Sustained growth
strong_growth = (rev_growth > 20).sustain(3)

# Combine
position = rev_high & strong_growth
position = rev_growth[position].is_largest(10)

# Rebalance on monthly revenue releases
report = sim(position, resample=rev, upload=False)
report.to_html("revenue_growth.html")
```

---

## See Also

- [SKILL.md](SKILL.md) - Overview and quick start
- [dataframe-reference.md](dataframe-reference.md) - FinLabDataFrame methods
- [backtesting-reference.md](backtesting-reference.md) - Complete `sim()` API
- [factor-examples.md](factor-examples.md) - 60+ complete examples
