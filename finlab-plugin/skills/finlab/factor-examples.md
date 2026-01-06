# Factor Examples and Strategy Reference

## Overview

This comprehensive guide provides practical examples of factor calculations, stock selection conditions, and complete trading strategies using the FinLab framework. All examples are organized by category for easy reference.

---

## Table of Contents

1. [Common Data Paths](#common-data-paths)
2. [Technical Indicators](#technical-indicators)
3. [Calculation Examples](#calculation-examples)
4. [Stock Selection Conditions](#stock-selection-conditions)
   - [Technical Analysis](#technical-analysis)
   - [Fundamental Analysis](#fundamental-analysis)
   - [Chip Analysis](#chip-analysis)
   - [Market Indicators](#market-indicators)
   - [Filter Tools](#filter-tools)
5. [Complete Strategy Examples](#complete-strategy-examples)

---

## Common Data Paths

```python
from finlab import data

# Price data
收盤價 = data.get("price:收盤價")
成交股數 = data.get("price:成交股數")

# Revenue data
當月營收 = data.get("monthly_revenue:當月營收")
去年同月增減 = data.get("monthly_revenue:去年同月增減(%)")

# Valuation metrics
本益比 = data.get("price_earning_ratio:本益比")
殖利率 = data.get("price_earning_ratio:殖利率(%)")
股價淨值比 = data.get("price_earning_ratio:股價淨值比")

# Fundamental features
ROE稅後 = data.get("fundamental_features:ROE稅後")
營業毛利率 = data.get("fundamental_features:營業毛利率")
自由現金流量 = data.get("fundamental_features:自由現金流量")

# Market value and institutional trading
市值 = data.get("etl:market_value")
外陸資買賣超股數 = data.get("institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)")
投信買賣超股數 = data.get("institutional_investors_trading_summary:投信買賣超股數")
```

---

## Technical Indicators

### Momentum Indicators

```python
from finlab import data

# ADX - Average Directional Index
adx = data.indicator("ADX", adjust_price=False, resample="D", timeperiod=14)

# RSI - Relative Strength Index
rsi = data.indicator("RSI", adjust_price=False, resample="D", timeperiod=14)

# MACD - Moving Average Convergence Divergence
macd, macdsignal, macdhist = data.indicator("MACD", adjust_price=False, resample="D",
                                              fastperiod=12, slowperiod=26, signalperiod=9)

# MOM - Momentum
mom = data.indicator("MOM", adjust_price=False, resample="D", timeperiod=10)

# ROC - Rate of Change
roc = data.indicator("ROC", adjust_price=False, resample="D", timeperiod=10)

# Stochastic Oscillator
slowk, slowd = data.indicator("STOCH", adjust_price=False, resample="D",
                               fastk_period=5, slowk_period=3, slowk_matype=0,
                               slowd_period=3, slowd_matype=0)

# Williams %R
willr = data.indicator("WILLR", adjust_price=False, resample="D", timeperiod=14)
```

### Moving Averages and Bands

```python
# Simple Moving Average
sma = data.indicator("SMA", adjust_price=False, resample="D", timeperiod=30)

# Exponential Moving Average
ema = data.indicator("EMA", adjust_price=False, resample="D", timeperiod=30)

# Bollinger Bands
upperband, middleband, lowerband = data.indicator("BBANDS", timeperiod=20,
                                                    nbdevup=2.0, nbdevdn=2.0, matype=0)

# Weighted Moving Average
wma = data.indicator("WMA", adjust_price=False, resample="D", timeperiod=30)

# TEMA - Triple Exponential Moving Average
tema = data.indicator("TEMA", adjust_price=False, resample="D", timeperiod=30)
```

### Volatility Indicators

```python
# ATR - Average True Range
atr = data.indicator("ATR", adjust_price=False, resample="D", timeperiod=14)

# NATR - Normalized ATR
natr = data.indicator("NATR", adjust_price=False, resample="D", timeperiod=14)

# TRANGE - True Range
trange = data.indicator("TRANGE", adjust_price=False, resample="D")
```

### Volume Indicators

```python
# AD - Chaikin A/D Line
ad = data.indicator("AD", adjust_price=False, resample="D")

# OBV - On Balance Volume
obv = data.indicator("OBV", adjust_price=False, resample="D")

# ADOSC - Chaikin A/D Oscillator
adosc = data.indicator("ADOSC", adjust_price=False, resample="D",
                        fastperiod=3, slowperiod=10)
```

---

## Calculation Examples

### Price-Based Calculations

```python
from finlab import data

收盤價 = data.get("price:收盤價")

# 60-day moving average
sma = 收盤價.average(60)

# 60-day maximum price
price_max = 收盤價.rolling(60).max()

# 60-day minimum price
price_min = 收盤價.rolling(60).min()

# 20-day price change percentage
price_pct = 收盤價.pct_change(periods=20)

# Price rising compared to 60 days ago
price_rise = 收盤價.rise(60)

# Price falling compared to 60 days ago
price_fall = 收盤價.fall(60)

# Price rising for 3 consecutive days
rise_sustain = 收盤價.rise().sustain(3)

# Price rising at least 2 out of last 3 days
rise_nsatisfy = 收盤價.rise().sustain(nwindow=3, nsatisfy=2)

# Price falling for 3 consecutive days
fall_sustain = 收盤價.fall().sustain(3)

# Top 10 highest prices in market
price_largest = 收盤價.is_largest(10)

# Top 10 lowest prices in market
price_smallest = 收盤價.is_smallest(10)
```

### Volume-Based Calculations

```python
成交股數 = data.get("price:成交股數")

# 20-day average volume
vol_ma = 成交股數.average(20)

# 20-day cumulative volume
vol_cumsum = 成交股數.rolling(20).sum()
```

### Revenue-Based Calculations

```python
當月營收 = data.get("monthly_revenue:當月營收")
去年同月增減 = data.get("monthly_revenue:去年同月增減(%)")

# 3-month average revenue
rev_ma = 當月營收.average(3)

# Revenue YoY growth > 20% for 3 consecutive months
rev_rise_sustain = (去年同月增減 > 20).sustain(3)

# Revenue YoY growth ranking (percentile)
rev_rise_nsatisfy = 去年同月增減.rank(pct=True, axis=1)
```

### Special Calculations

```python
# Align position to monthly revenue dates
rev = data.get("monthly_revenue:當月營收")
position = position.reindex(rev.index_str_to_date().index, method="ffill")

# Replace infinity with NaN
inf_ratio = (data.get("financial_statement:研究發展費") /
             data.get("financial_statement:營業收入淨額")).replace(np.inf, np.nan)

# Inventory - large holders (>400 lots)
inventory = data.get("inventory")
boss_inventory = inventory[
    (inventory.持股分級.astype(int) >= 12) &
    (inventory.持股分級.astype(int) <= 15)
].reset_index().groupby(["date", "stock_id"]).agg({
    "占集保庫存數比例": "sum"
}).reset_index().pivot("date", "stock_id")["占集保庫存數比例"]

# Inventory - retail investors (<50 lots)
small_inv = inventory[
    (inventory.持股分級.astype(int) <= 8)
].reset_index().groupby(["date", "stock_id"]).agg({
    "占集保庫存數比例": "sum"
}).reset_index().pivot("date", "stock_id")["占集保庫存數比例"]
```

---

## Stock Selection Conditions

### Technical Analysis

#### Moving Average Strategies

```python
收盤價 = data.get("price:收盤價")

# Price above 60-day MA
sma60 = 收盤價 > 收盤價.average(60)

# Price breaks above 60-day MA
sma60_breakout = (收盤價 > 收盤價.average(60)) & (收盤價.shift() < 收盤價.average(60).shift())

# Price breaks below 60-day MA
sma60_breakdown = (收盤價 < 收盤價.average(60)) & (收盤價.shift() > 收盤價.average(60).shift())

# Bullish alignment (5/10/20 MA)
long_ma_pattern = (收盤價 > 收盤價.average(5)) & (收盤價 > 收盤價.average(10)) & (收盤價 > 收盤價.average(20))

# Bearish alignment (5/10/20 MA)
short_ma_pattern = (收盤價 < 收盤價.average(5)) & (收盤價 < 收盤價.average(10)) & (收盤價 < 收盤價.average(20))
```

#### Price Extreme Conditions

```python
# New 5-day high
new_high = (收盤價 / 收盤價.rolling(5).max()) == 1

# New 5-day low
new_low = (收盤價 / 收盤價.rolling(5).min()) == 1

# Making new 3-day highs for 5 consecutive days
price_boost = ((收盤價 / 收盤價.rolling(3).max()) == 1).sustain(5)

# Making new 3-day lows for 5 consecutive days
price_crash = ((收盤價 / 收盤價.rolling(3).min()) == 1).sustain(5)

# Not making new 3-day highs for 5 consecutive days
price_pressure = ((收盤價 / 收盤價.rolling(3).max()) < 1).sustain(5)

# Not making new 3-day lows for 5 consecutive days
price_support = ((收盤價 / 收盤價.rolling(3).min()) > 1).sustain(5)

# 20-day price change less than 20%
price_pct_cond = 收盤價.pct_change(periods=20) < 0.20
```

#### Volume Conditions

```python
成交股數 = data.get("price:成交股數")

# 20-day average volume > 1,000,000
vol_ma = 成交股數.average(20) > 1000000

# Volume above 60-day MA
vol_ma = 成交股數 > 成交股數.average(60)

# Volume making new 3-day highs for 5 consecutive days
vol_boost = ((成交股數 / 成交股數.rolling(3).max()) == 1).sustain(5)

# Volume making new 3-day lows for 5 consecutive days
vol_crash = ((成交股數 / 成交股數.rolling(3).min()) == 1).sustain(5)
```

#### Technical Indicator Conditions

```python
# RSI golden cross
rsi1 = data.indicator("RSI", adjust_price=False, resample="D", timeperiod=14)
rsi2 = data.indicator("RSI", adjust_price=False, resample="D", timeperiod=28)
rsi_gold_cross = (rsi1 > rsi2) & (rsi1.shift() < rsi2.shift())

# RSI overbought for 5 consecutive days
rsi = data.indicator("RSI", adjust_price=False, resample="D", timeperiod=5)
rsi_high_trend = (rsi > 80).sustain(5)

# KD golden cross
slowk, slowd = data.indicator("STOCH", adjust_price=False, resample="D",
                               fastk_period=5, slowk_period=3, slowk_matype=0,
                               slowd_period=3, slowd_matype=0)
kd_gold_cross = (slowk > slowd) & (slowk.shift() < slowd.shift())

# 10-day volatility (ATR)
adj_close = data.get("etl:adj_close")
volatility = data.indicator("ATR", adjust_price=True, resample="D", timeperiod=10) / adj_close

# Breaking above Keltner Channel upper band
ema = data.indicator("EMA", adjust_price=True, resample="D", timeperiod=10)
atr = data.indicator("ATR", adjust_price=True, resample="D", timeperiod=10)
keltner_up = ema + 2 * atr
cond = (adj_close > keltner_up) & (adj_close.shift() < keltner_up.shift())

# Breaking above Bollinger upper band
upperband, middleband, lowerband = data.indicator("BBANDS", timeperiod=10)
cond = (收盤價 > upperband) & (收盤價.shift() < upperband.shift())

# Breaking below Bollinger lower band
cond = (收盤價 < lowerband) & (收盤價.shift() > lowerband.shift())
```

---

### Fundamental Analysis

#### Revenue Growth

```python
去年同月增減 = data.get("monthly_revenue:去年同月增減(%)")
上月比較增減 = data.get("monthly_revenue:上月比較增減(%)")
當月營收 = data.get("monthly_revenue:當月營收")

# Revenue YoY growth > 30%
rev_yy = 去年同月增減 > 30

# Revenue MoM growth > 30%
rev_mm = 上月比較增減 > 30

# 3-month average revenue > 12-month average revenue
rev_sl_compare = (當月營收.average(3) > 當月營收.average(12))

# 3-month average revenue YoY growth > 12-month average revenue YoY growth
rev_sl_growth = 當月營收.average(3).pct_change(12) > 當月營收.average(12).pct_change(12)

# 2-month average revenue at 12-month high
rev_new_high = (當月營收.average(2) / 當月營收.average(2).rolling(12, min_periods=6).max()) == 1

# At least 2 out of last 3 months with YoY growth > 20%
rev_rise_nsatisfy = (去年同月增減 > 20).sustain(nwindow=3, nsatisfy=2)

# Revenue YoY growth ranking > 80th percentile
rev_rise_nsatisfy = 去年同月增減.rank(pct=True, axis=1) > 0.80
```

#### Valuation Metrics

```python
本益比 = data.get("price_earning_ratio:本益比")
股價淨值比 = data.get("price_earning_ratio:股價淨值比")
殖利率 = data.get("price_earning_ratio:殖利率(%)")

# PE ratio between 5 and 20
pe_range = (5 <= 本益比) & (本益比 <= 20)

# PB ratio between 0.5 and 2
pb_range = (0.5 <= 股價淨值比) & (股價淨值比 <= 2)

# Dividend yield between 3% and 10%
yield_range = (3 <= 殖利率) & (殖利率 <= 10)
```

#### Profitability Metrics

```python
營運現金流 = data.get("fundamental_features:營運現金流")
營業毛利率 = data.get("fundamental_features:營業毛利率")
營業利益率 = data.get("fundamental_features:營業利益率")
稅前淨利率 = data.get("fundamental_features:稅前淨利率")
稅後淨利率 = data.get("fundamental_features:稅後淨利率")
業外收支營收率 = data.get("fundamental_features:業外收支營收率")
每股盈餘 = data.get("financial_statement:每股盈餘")
ROA綜合損益 = data.get("fundamental_features:ROA綜合損益")
ROE綜合損益 = data.get("fundamental_features:ROE綜合損益")

# Operating cash flow > 0 for 1 quarter
ope_cashflow_trend = (營運現金流 > 0).sustain(1)

# Gross margin > 3% for 1 quarter
gpm_trend = (營業毛利率 > 3).sustain(1)

# Operating margin > 3% for 1 quarter
opm_trend = (營業利益率 > 3).sustain(1)

# Pre-tax margin > 3% for 1 quarter
btpm_trend = (稅前淨利率 > 3).sustain(1)

# After-tax margin > 3% for 1 quarter
atpm_trend = (稅後淨利率 > 3).sustain(1)

# Non-operating income ratio > 3% for 1 quarter
opm_trend = (業外收支營收率 > 3).sustain(1)

# EPS > 0 for 4 consecutive quarters
eps_trend = (每股盈餘 > 0).sustain(4)

# ROA > 0% for 4 consecutive quarters
roa_trend = (ROA綜合損益 > 0).sustain(4)

# ROE > 0% for 4 consecutive quarters
roe_trend = (ROE綜合損益 > 0).sustain(4)
```

#### Leverage Metrics

```python
負債比率 = data.get("fundamental_features:負債比率")

# Debt ratio < 50% for 4 consecutive quarters
debt_trend = (負債比率 < 50).sustain(4)
```

---

### Chip Analysis

#### Institutional Trading

```python
from finlab import data

# Foreign institutional net buy ratio > 10% in 1 day
iit = data.get("institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)")
vol = data.get("price:成交股數")
iit_ratio = iit.rolling(1).sum() / vol.rolling(1).sum() > 0.1

# Investment trust net buy ratio > 10% in 1 day
投信買賣超股數 = data.get("institutional_investors_trading_summary:投信買賣超股數")
成交股數 = data.get("price:成交股數")
ict_ratio = 投信買賣超股數.rolling(1).sum() / 成交股數.rolling(1).sum() > 0.1

# Foreign net buy > 200,000 shares for 2 consecutive days
itt = data.get("institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)")
itt_trend = (itt > 200000).sustain(2)

# Investment trust net buy > 200,000 shares for 2 consecutive days
ict_trend = (投信買賣超股數 > 200000).sustain(2)
```

#### Shareholding Distribution

```python
inventory = data.get("inventory")
董監持有股數占比 = data.get("internal_equity_changes:董監持有股數占比")

# Large holders (>400 lots) shareholding >= 30%
boss_inv = inventory[
    (inventory.持股分級.astype(int) >= 12) &
    (inventory.持股分級.astype(int) <= 15)
].reset_index().groupby(["date", "stock_id"]).agg({
    "占集保庫存數比例": "sum"
}).reset_index().pivot("date", "stock_id")["占集保庫存數比例"] >= 30

# Large holders (>800 lots) shareholding >= 30%
boss_inv = inventory[
    (inventory.持股分級.astype(int) >= 14) &
    (inventory.持股分級.astype(int) <= 15)
].reset_index().groupby(["date", "stock_id"]).agg({
    "占集保庫存數比例": "sum"
}).reset_index().pivot("date", "stock_id")["占集保庫存數比例"] >= 30

# Large holders (>400 lots) increasing for 3 consecutive periods
from finlab import dataframe
boss_inv_trend = dataframe.FinlabDataFrame(
    inventory[
        (inventory.持股分級.astype(int) >= 12) &
        (inventory.持股分級.astype(int) <= 15)
    ].reset_index().groupby(["date", "stock_id"]).agg({
        "占集保庫存數比例": "sum"
    }).reset_index().pivot("date", "stock_id")["占集保庫存數比例"]
).rise().sustain(3)

# Retail investors (<50 lots) shareholding <= 30%
small_inv = inventory[
    (inventory.持股分級.astype(int) <= 8)
].reset_index().groupby(["date", "stock_id"]).agg({
    "占集保庫存數比例": "sum"
}).reset_index().pivot("date", "stock_id")["占集保庫存數比例"] <= 30

# Retail investors (<50 lots) decreasing for 3 consecutive periods
from finlab import dataframe
small_inv_trend = dataframe.FinlabDataFrame(
    inventory[
        (inventory.持股分級.astype(int) <= 8)
    ].reset_index().groupby(["date", "stock_id"]).agg({
        "占集保庫存數比例": "sum"
    }).reset_index().pivot("date", "stock_id")["占集保庫存數比例"]
).fall().sustain(3)

# Total number of shareholders decreasing for 3 consecutive periods
inv_small_people_trend = dataframe.FinlabDataFrame(
    inventory[
        (inventory.人數.astype(int) == 17)
    ].reset_index().groupby(["date", "stock_id"]).agg({
        "人數": "sum"
    }).reset_index().pivot("date", "stock_id")["人數"]
).fall().sustain(3)

# Director/supervisor shareholding > 30%
boss_hold = 董監持有股數占比 > 30

# Director/supervisor shareholding increasing compared to 1 month ago
boss_hold_rise = 董監持有股數占比.rise(1)
```

#### Day Trading and Margin

```python
當日沖銷交易成交股數 = data.get("intraday_trading:當日沖銷交易成交股數")
成交股數 = data.get("price:成交股數")
融資使用率 = data.get("margin_transactions:融資使用率")
融券使用率 = data.get("margin_transactions:融券使用率")
融券今日餘額 = data.get("margin_transactions:融券今日餘額")
融資今日餘額 = data.get("margin_transactions:融資今日餘額")

# Day trading ratio < 10%
day_trade_ratio = 當日沖銷交易成交股數 / 成交股數 / 2 < 0.1

# Margin utilization > 0% for 1 day
margin_used_raio = (融資使用率 > 0).sustain(1)

# Short selling utilization > 0% for 1 day
margin_sell_used_raio = (融券使用率 > 0).sustain(1)

# Short/Margin ratio > 0% for 1 day
margin_trend = (融券今日餘額 / 融資今日餘額 > 0).sustain(1)
```

---

### Market Indicators

```python
# ADLs (Advance-Decline Line with Smoothing)
def ADLs_position(short_par=20, long_par=55):
    close = data.get("price:收盤價")
    close_diff = close.diff()
    total_stocks = (~close.isna()).sum(1)
    rise_stocks = (close_diff > 0).sum(1)
    ADLs = rise_stocks / total_stocks - 0.5
    short_ADLs_ma = ADLs.rolling(short_par).mean()
    long_ADLs_ma = ADLs.rolling(long_par).mean()
    cond = ~close.isna()
    cond1 = short_ADLs_ma >= long_ADLs_ma
    position = cond & cond1
    return position

# VIX (Volatility Index)
def vix_position(short_par=5, long_par=20):
    df = data.get("world_index:open")
    vix = df["^VIX"].dropna()
    short_vix_ma = vix.rolling(short_par).mean()
    long_vix_ma = vix.rolling(long_par).mean()
    close = data.get("price:收盤價")
    cond = ~close.isna()
    cond1 = short_vix_ma <= long_vix_ma
    cond1 = cond1.reindex(close.index)
    position = cond & cond1
    return position

# Market Long/Short Alignment Count
def ls_order_position(short=5, mid=10, long=30):
    close = data.get("price:收盤價")
    short_ma = close.average(short)
    mid_ma = close.average(mid)
    long_ma = close.average(long)
    long_order = (short_ma >= mid_ma) & (mid_ma >= long_ma)
    long_order = long_order.sum(1)
    short_order = (short_ma < mid_ma) & (mid_ma < long_ma)
    short_order = short_order.sum(1)
    entry = long_order > short_order
    cond = ~close.isna()
    position = cond & entry
    return position

# Margin Maintenance Ratio
def margin_position(short_par=5, long_par=30):
    融資券總餘額 = data.get("margin_balance:融資券總餘額").fillna(method="ffill")
    融資今日餘額 = data.get("margin_transactions:融資今日餘額")
    close = data.get("price:收盤價")
    融資總餘額 = 融資券總餘額[["上市融資交易金額", "上櫃融資交易金額"]].sum(axis=1)
    融資餘額市值 = (融資今日餘額 * close * 1000).sum(axis=1)[融資今日餘額.index]
    mt_rate = (融資餘額市值 / 融資總餘額)
    mt_rate = mt_rate.dropna()
    short_ma = mt_rate.rolling(short_par).mean()
    long_ma = mt_rate.rolling(long_par).mean()
    entry = short_ma >= long_ma
    cond = ~close.isna()
    position = cond & entry
    return position
```

---

### Filter Tools

```python
from finlab import data

# Filter out attention stocks
noticed_stock_filter = data.get("etl:noticed_stock_filter")

# Filter out disposal stocks
disposal_stock_filter = data.get("etl:disposal_stock_filter")

# Filter out full cash delivery stocks
full_cash_delivery_stock_filter = data.get("etl:full_cash_delivery_stock_filter")

# Filter out KY stocks
sc = data.get("security_categories")
position_col = position.columns
ky_filter = position_col[~position_col.isin(list(sc[sc["name"].str.contains("KY")]["stock_id"]))]
position = position[ky_filter]

# Limit backtest to specific industry
data.set_universe(market="TSE_OTC", category="建材營造")
```

---

## Complete Strategy Examples

### 1. New High Strategy

Select stocks making 250-day new highs.

```python
from finlab import data
from finlab.backtest import sim

close = data.get("price:收盤價")
position = (close == close.rolling(250).max())
sim(position, resample="M", name="創年新高策略")
```

---

### 2. Revenue Momentum Strategy

Select stocks with strong recent revenue performance.

```python
from finlab import data
from finlab.backtest import sim
import pandas as pd

rev = data.get("monthly_revenue:當月營收")
rev_rf = data.get("monthly_revenue:去年同月增減(%)")
vol = data.get("price:成交股數") / 1000

rev_recent_3 = rev.rolling(3).sum()
vol_avg = vol.average(10)

cond1 = (rev_recent_3 / rev_recent_3.rolling(24, min_periods=12).max()) == 1
cond2 = vol_avg > 300
cond_all = cond1 & cond2

result = rev_rf * (cond_all)
position = result[result > 0].is_largest(10).reindex(rev.index_str_to_date().index, method="ffill")

sim(position=position, stop_loss=0.3, position_limit=0.1)
```

---

### 3. Cash Flow Strategy

Select stocks with positive cash flows across all categories.

```python
from finlab import data
from finlab.backtest import sim

營業現金流 = data.get("financial_statement:營業活動之淨現金流入_流出")
投資現金流 = data.get("financial_statement:投資活動之淨現金流入_流出")
融資現金流 = data.get("financial_statement:籌資活動之淨現金流入_流出")

position = (營業現金流 > 0) & (投資現金流 > 0) & (融資現金流 > 0)
report = sim(position, resample="M", name="現金流正數")
```

---

### 4. PEG Strategy

Price-Earnings to Growth ratio strategy.

```python
from finlab import data
from finlab.backtest import sim

pe = data.get("price_earning_ratio:本益比")
rev = data.get("monthly_revenue:當月營收")
rev_ma3 = rev.average(3)
rev_ma12 = rev.average(12)
營業利益成長率 = data.get("fundamental_features:營業利益成長率")

peg = (pe / 營業利益成長率)
cond1 = rev_ma3 / rev_ma12 > 1.1
cond2 = rev / rev.shift(1) > 0.9
cond_all = cond1 & cond2

result = peg * (cond_all)
position = result[result > 0].is_smallest(10).reindex(rev.index_str_to_date().index, method="ffill")

sim(position=position, name="peg_rev", fee_ratio=1.425/1000/3, stop_loss=0.1)
```

---

### 5. Momentum + ROE Filter Strategy

Combine price momentum with ROE filter.

```python
from finlab import data
from finlab.backtest import sim

# Download ROE and closing price
roe = data.get("fundamental_features:ROE稅後")
close = data.get("price:收盤價")

position = ((close / close.shift(60)).is_largest(30) & (roe > 0))

# Backtest, rebalance monthly (M)
report = sim(position, resample="M")
```

---

### 6. Low PB Strategy

Price-to-Book ratio strategy with technical filter.

```python
from finlab import data
from finlab.backtest import sim

pb = data.get("price_earning_ratio:股價淨值比")
close = data.get("price:收盤價")

buy = (1 / (pb * close) * (close > close.average(60)) * (close > 5)).is_largest(20)
sim(buy, resample="Q")
```

---

### 7. Triple RSI Strategy

Advanced RSI-based strategy with multiple timeframes.

```python
from finlab import data
from finlab.backtest import sim
import pandas as pd
from finlab import dataframe

close = data.get("price:收盤價")
roe = data.get("fundamental_features:ROE稅後")

rsi1 = data.indicator("RSI", timeperiod=20)
rsi2 = data.indicator("RSI", freq="D", timeperiod=60)
rsi3 = data.indicator("RSI", freq="D", timeperiod=120)

buy = (rsi3 > 55) & (rsi1 / rsi1.shift(3) > 1.02) & (roe > 0) & \
      dataframe.FinlabDataFrame(rsi1 > 75).sustain(3) & (rsi2 < 75)
sell = buy.shift(60) | (close < close.average(60))

position = pd.DataFrame(np.nan, index=buy.index, columns=buy.columns)
position[buy] = 1
position[sell] = 0
position = position.ffill().fillna(0)

report = sim(position.loc["2014":], resample="W")
```

---

### 8. High RSI Strategy

Simple high RSI momentum strategy.

```python
from finlab import data
from finlab.backtest import sim

rsi = data.indicator("RSI")
position = rsi.is_largest(20)
report = sim(position, resample="W", name="高RSI策略")
```

---

### 9. Entry/Exit Signal Example

Using hold_until for explicit entry and exit signals.

```python
from finlab import data
from finlab.backtest import sim

close = data.get("price:收盤價")
pb = data.get("price_earning_ratio:股價淨值比")

sma20 = close.average(20)
sma60 = close.average(60)

entries = close > sma20
exits = close < sma60

position = entries.hold_until(exits, nstocks_limit=10, rank=-pb)
sim(position)
```

---

### 10. Long/Short Strategy

Example of simultaneous long and short positions.

```python
from finlab import data
from finlab import backtest

close = data.get("price:收盤價")
position = close < 0  # Start with all False

position["2330"] = 0.5   # Long TSMC with 50% weight
position["1101"] = -0.5  # Short Taiwan Cement with 50% weight

report = backtest.sim(position)
```

---

## Best Practices

1. **Use vectorized operations** - Never use for loops on FinlabDataFrame
2. **Set appropriate resample periods** - Use 'M', 'Q', or revenue.index to avoid overtrading
3. **Combine multiple factors** - Single factor strategies are often less robust
4. **Apply filters** - Remove special status stocks (disposal, attention, full cash delivery)
5. **Control position size** - Use position_limit and nstocks_limit
6. **Set stop loss/take profit** - Protect against large losses
7. **Universe filtering** - Use data.universe() to scope data.get() calls only
8. **Proper alignment** - Let FinlabDataFrame handle index/column alignment automatically

---

## Related References

- [FinlabDataFrame Reference](dataframe-reference.md) - Enhanced DataFrame methods
- [Backtesting Reference](backtesting-reference.md) - Backtest your strategies
- [Data Reference](data-reference.md) - Complete data catalog
- [Factor Analysis Reference](factor-analysis-reference.md) - Analyze factor performance
- [Machine Learning Reference](machine-learning-reference.md) - ML-based strategies
