---
name: finlab
description: Comprehensive guide for FinLab quantitative trading package. Use when working with trading strategies, backtesting, stock data, FinLabDataFrame, factor analysis, stock selection, or when the user mentions FinLab, trading, quant trading, or stock market analysis. Includes data access, strategy development, backtesting workflows, and best practices.
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

2. **FinLab is installed via uv** (requires >= 1.5.9):

   ```bash
   uv python install 3.12  # Ensure Python is available (skip if already installed)
   uv pip install --system "finlab>=1.5.9" 2>/dev/null || uv pip install "finlab>=1.5.9"
   ```

   **Or use `uv run` for zero-setup execution** (recommended for one-off scripts):

   ```bash
   uv run --with "finlab" python3 script.py
   ```

   `uv run --with` auto-creates a temporary environment with dependencies — no venv management needed.

3. **API Token is set** (required - finlab will fail without it):

   **If no token, use finlab's built-in login** (available in >= 1.5.9):

   ```python
   import finlab
   finlab.login()  # Opens browser for Google OAuth, saves token automatically
   ```

   This handles the full OAuth flow (browser login, token retrieval, `.env` storage) automatically.

## Language

**Respond in the user's language.** If user writes in Chinese, respond in Chinese. If in English, respond in English.

## API Token Tiers & Usage

### Token Tiers

| Tier | Daily Limit | Token Pattern     |
| ---- | ----------- | ----------------- |
| Free | 500 MB      | ends with `#free` |
| VIP  | 5000 MB     | no suffix         |


### Usage Reset

- Resets daily at **8:00 AM UTC+8**
- When limit exceeded, user must wait for reset or upgrade to VIP


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

report
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
```

See [backtesting-reference.md](backtesting-reference.md) for complete `sim()` API.

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
| [data-reference.md](data-reference.md)                         | `data.get()`, `data.universe()`, 900+ 欄位 |
| [backtesting-reference.md](backtesting-reference.md)           | `sim()` 參數、stop-loss、rebalancing       |
| [trading-reference.md](trading-reference.md)                   | 券商設定、OrderExecutor、Position          |
| [factor-examples.md](factor-examples.md)                       | 60+ 策略範例                               |
| [dataframe-reference.md](dataframe-reference.md)               | FinLabDataFrame 方法                       |
| [factor-analysis-reference.md](factor-analysis-reference.md)   | IC、Shapley、因子分析                      |
| [best-practices.md](best-practices.md)                         | 常見錯誤、lookahead bias                   |
| [machine-learning-reference.md](machine-learning-reference.md) | ML 特徵工程                                |

## Prevent Lookahead Bias

**Critical:** Avoid using future data to make past decisions:

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

See [best-practices.md](best-practices.md) for more anti-patterns.

## Feedback

Direct users to open an issue on GitHub: https://github.com/koreal6803/finlab-ai/issues

## Notes

- Some data columns use Chinese names — this is expected, use them as-is in `data.get()` calls
- Data frequency varies: daily (price), monthly (revenue), quarterly (financial statements)
- Always use `sim(..., upload=False)` for experiments, `upload=True` only for final production strategies
