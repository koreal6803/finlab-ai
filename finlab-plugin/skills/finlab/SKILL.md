---
name: finlab
description: Comprehensive guide for FinLab quantitative trading package for Taiwan stock market (台股). Use when working with trading strategies, backtesting, Taiwan stock data, FinLabDataFrame, factor analysis, stock selection, or when the user mentions FinLab, trading, 回測, 策略, 台股, quant trading, or stock market analysis. Includes data access, strategy development, backtesting workflows, and best practices.
allowed-tools: Read, Grep, Glob, Bash
---

# FinLab Quantitative Trading Package

## Overview

FinLab is a comprehensive Python package for quantitative trading strategy development, backtesting, and financial data analysis, specifically designed for the Taiwan stock market (TSE/OTC, 台股). It provides:

- **Extensive Data Access**: Price data, financial statements, monthly revenue, valuation metrics, institutional trading, technical indicators
- **FinLabDataFrame**: Enhanced pandas DataFrame with trading-specific methods (`is_largest`, `is_smallest`, `rise`, `fall`, `sustain`, `hold_until`)
- **Backtesting Engine**: Robust `sim()` function with rebalancing, transaction costs, stop-loss/take-profit, risk management
- **Factor Analysis**: IC calculation, Shapley values, centrality analysis, regression trends
- **Machine Learning**: Feature engineering for TA-Lib indicators, label generation for returns

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

# 5. Print metrics
print(report.metrics.annual_return())
print(report.metrics.sharpe_ratio())
print(report.metrics.max_drawdown())
report
```

## Core Workflow: 4-Step Strategy Development

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

See [data-reference.md](data-reference.md) for complete data catalog.

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

# Extract metrics
print(f"Annual Return: {report.metrics.annual_return():.2%}")
print(f"Sharpe Ratio: {report.metrics.sharpe_ratio():.2f}")
print(f"Max Drawdown: {report.metrics.max_drawdown():.2%}")
```

See [backtesting-reference.md](backtesting-reference.md) for complete `sim()` API.

## Documentation Structure

This skill includes comprehensive reference documentation:

- **[data-reference.md](data-reference.md)**: Complete data catalog (900+ columns across 80+ tables), `data.get()` usage, `data.universe()` filtering
- **[backtesting-reference.md](backtesting-reference.md)**: `sim()` function API, all parameters, resampling strategies, metric extraction
- **[factor-examples.md](factor-examples.md)**: 60+ complete factor examples (momentum, value, quality, growth, technical)
- **[dataframe-reference.md](dataframe-reference.md)**: All FinLabDataFrame methods with signatures and examples
- **[factor-analysis-reference.md](factor-analysis-reference.md)**: Factor analysis tools (IC, Shapley values, centrality)
- **[best-practices.md](best-practices.md)**: Coding patterns, anti-patterns, future data pollution prevention
- **[machine-learning-reference.md](machine-learning-reference.md)**: ML feature engineering and label generation

## When to Use Each Reference

| Task | Reference File |
|------|----------------|
| Find available data sources | [data-reference.md](data-reference.md) |
| Fetch price, revenue, financial statement data | [data-reference.md](data-reference.md) |
| Filter stocks by industry/market | [data-reference.md](data-reference.md) |
| Configure backtest parameters | [backtesting-reference.md](backtesting-reference.md) |
| Set stop-loss, take-profit, rebalancing | [backtesting-reference.md](backtesting-reference.md) |
| Find strategy examples | [factor-examples.md](factor-examples.md) |
| Calculate moving averages, trends | [dataframe-reference.md](dataframe-reference.md) |
| Select top N stocks | [dataframe-reference.md](dataframe-reference.md) |
| Combine entry/exit signals | [dataframe-reference.md](dataframe-reference.md) |
| Analyze factor performance | [factor-analysis-reference.md](factor-analysis-reference.md) |
| Avoid common mistakes | [best-practices.md](best-practices.md) |
| Prevent lookahead bias | [best-practices.md](best-practices.md) |
| Build ML models for trading | [machine-learning-reference.md](machine-learning-reference.md) |

## Common Use Cases

### Use Case 1: Value + Momentum Strategy

```python
from finlab import data
from finlab.backtest import sim

# Value: Low P/B ratio
pb = data.get("price_earning_ratio:股價淨值比")
low_pb = pb.rank(axis=1, pct=True) < 0.3

# Momentum: Rising price
close = data.get("price:收盤價")
momentum = close.rise(20)

# Liquidity filter
vol = data.get("price:成交股數")
liquid = vol.average(20) > 500*1000

# Combine
position = low_pb & momentum & liquid
position = pb[position].is_smallest(15)

report = sim(position, resample="M", stop_loss=0.1)
```

### Use Case 2: Monthly Revenue Growth Strategy

```python
from finlab import data
from finlab.backtest import sim

rev = data.get("monthly_revenue:當月營收")
rev_growth = data.get("monthly_revenue:去年同月增減(%)")

# Revenue at new high
rev_ma3 = rev.average(3)
rev_high = (rev_ma3 / rev_ma3.rolling(12).max()) == 1

# Strong growth
strong_growth = (rev_growth > 20).sustain(3)

position = rev_high & strong_growth
position = rev_growth[position].is_largest(10)

# Use monthly revenue index for rebalancing
position_resampled = position.reindex(rev.index_str_to_date().index, method="ffill")
report = sim(position_resampled)
```

### Use Case 3: Technical Indicator Strategy

```python
from finlab import data
from finlab.backtest import sim

close = data.get("price:收盤價")
rsi = data.indicator("RSI", timeperiod=14)

# RSI golden cross
rsi_short = data.indicator("RSI", timeperiod=7)
rsi_long = data.indicator("RSI", timeperiod=21)
golden_cross = (rsi_short > rsi_long) & (rsi_short.shift() < rsi_long.shift())

# Above moving average
sma60 = close.average(60)
uptrend = close > sma60

position = golden_cross & uptrend & (rsi < 70)
position = position[position].is_smallest(20)

report = sim(position, resample="W")
```

## Key Concepts

### FinLabDataFrame Automatic Alignment

FinLabDataFrame automatically aligns indices and columns during operations:

```python
close = data.get("price:收盤價")  # Daily data
revenue = data.get("monthly_revenue:當月營收")  # Monthly data

# Automatically aligns - no manual reindexing needed
position = close > close.average(60) & (revenue > revenue.shift(1))
```

### Prevent Future Data Pollution

**Critical:** Avoid lookahead bias (using future data to make past decisions):

```python
# ✅ GOOD: Use shift(1) to get previous value
prev_close = close.shift(1)

# ❌ BAD: Don't use iloc[-2] (can cause lookahead)
# prev_close = close.iloc[-2]  # WRONG

# ✅ GOOD: Leave index as-is even with strings like "2025Q1"
# FinLabDataFrame aligns by shape automatically

# ❌ BAD: Don't manually assign to df.index
# df.index = new_index  # FORBIDDEN
```

See [best-practices.md](best-practices.md) for comprehensive anti-patterns.

## Installation & Setup

**API Token Required:** Before using FinLab, check if `FINLAB_API_TOKEN` is set. If not, ask the user to:
1. Get token from https://ai.finlab.tw/api_token/
2. Provide it so you can help set the environment variable

```bash
# Set environment variable (add to ~/.zshrc or ~/.bashrc)
export FINLAB_API_TOKEN="your_token_here"
```

```python
# Install finlab
pip install finlab

# Import commonly used modules (token auto-loaded from environment)
from finlab import data
from finlab.backtest import sim
from finlab.dataframe import FinLabDataFrame
```

## Getting Help

- For complete data catalog: see [data-reference.md](data-reference.md)
- For factor examples: see [factor-examples.md](factor-examples.md)
- For best practices: see [best-practices.md](best-practices.md)
- For backtesting parameters: see [backtesting-reference.md](backtesting-reference.md)

## Notes

- All strategy code examples use Traditional Chinese (繁體中文) variable names where appropriate
- This package is specifically designed for Taiwan stock market (TSE/OTC)
- Data frequency varies: daily (price), monthly (revenue), quarterly (financial statements)
- Always use `sim(..., upload=False)` for experiments, `upload=True` only for final production strategies
