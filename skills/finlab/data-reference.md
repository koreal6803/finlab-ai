# Data Reference

## Overview

The FinLab data module provides comprehensive access to stock market data, including prices, financial statements, fundamental metrics, institutional trading, and economic indicators. Use `data.get()` to retrieve any dataset using a simple path-based syntax.

---

## Table of Contents

- [Usage](#usage) - Basic data retrieval with `data.get()`
- [Data Discovery](#data-discovery) - Find datasets with `data.search()`
- [Batch Download](#batch-download) - Parallel fetch with `data.gets()`
- [User Role & Quota](#user-role--quota) - `data.get_role()` / `data.is_vip()`
- [DataContext Override](#datacontext-override) - Temporarily scope data state
- [Technical Indicators](#technical-indicators) - Compute indicators with `data.indicator()`
- [Universe Filtering](#universe-filtering) - Filter by market/category/index
- [Data Catalog](#data-catalog) - Complete dataset reference
- [Storage Configuration](#storage-configuration) - Cache and storage settings
- [Plotting Data](#plotting-data) - Visualization examples

---

## Usage

### Basic Syntax

```python
from finlab import data

# Retrieve data using TABLE:COLUMN format
df = data.get('price:收盤價')

# Use data.search() to find available ETL data
# data.search('inventory')  # Discover available inventory ETL datasets
boss_ratio = data.get('etl:inventory:大於四百張佔比')
```

### Data Path Construction

The path is constructed using colons (`:`) to navigate hierarchical data structures:

**Format:**
- `<TABLE>:<COLUMN>` - For tables with multiple columns
- `<TABLE>` - For tables without column structure

**Example:**
```python
# Get closing price
closing_price = data.get('price:收盤價')

# Get earnings per share
eps = data.get('financial_statement:每股盈餘')

# Get foreign investor trading volume
foreign_investment = data.get('institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)')
```

### Common Field Names

| Term | Field |
|------|-------|
| EPS | `financial_statement:每股盈餘` |
| 本益比 | `price_earning_ratio:本益比` |
| 股價淨值比 | `price_earning_ratio:股價淨值比` |
| 殖利率 | `price_earning_ratio:殖利率(%)` |
| ROE | `fundamental_features:ROE稅後` |
| 毛利率 | `fundamental_features:營業毛利率` |
| 月營收 | `monthly_revenue:當月營收` |
| 營收年增率 | `monthly_revenue:去年同月增減(%)` |

---

## Data Discovery

Use `data.search()` to programmatically find datasets from the Data Catalog.

**Signature:**
```python
data.search(keyword: str = None, market: str = 'tw') -> list
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | str | None | Filter datasets by keyword (case-insensitive substring match). Returns all if omitted. |
| `market` | str | 'tw' | Market to search: `'tw'`, `'us'`, or `'all'` (both markets). |

**Returns:** List of `"table:column"` strings, usable directly with `data.get()`.

**Examples:**
```python
from finlab import data

# List all available datasets
all_data = data.search()

# Search by keyword
data.search('收盤')    # ['price:收盤價']
data.search('營收')    # ['monthly_revenue:當月營收', ...]

# Search US market data (testing)
data.search('close', market='us')

# Use result with data.get()
results = data.search('收盤')
df = data.get(results[0])
```

**Note:** `data.get()` emits an 80% usage warning before quota is exhausted *(v1.5.9)*, so long-running notebooks surface quota issues early rather than failing mid-run.

---

## Batch Download

*(v2.0.0)* Fetch many datasets in one call. Returns a tuple in the order requested; shows a progress bar (terminal ANSI / Jupyter HTML, auto-detected).

```python
from finlab import data

price, volume, pb, roe = data.gets(
    'price:收盤價',
    'price:成交股數',
    'price_earning_ratio:股價淨值比',
    'fundamental_features:ROE稅後',
)
```

---

## User Role & Quota

*(v1.5.11)* Query the current session's user tier programmatically.

```python
from finlab import data

data.get_role()   # 'free' | 'vip' | 'admin' ...
data.is_vip()     # bool — True if current token has VIP quota
```

**Use case:** Skip expensive operations or fall back to smaller universes when running under the free tier (500 MB/day vs VIP's 5000 MB/day).

---

## DataContext Override

*(v2.0.0)* `data.override()` is a context manager that temporarily overrides global data state (universe, truncate window, storage flags, etc.) without leaking into the rest of the process. This replaces the older pattern of manually saving and restoring `data.truncate_start` / `data.force_cloud_download` globals and lays groundwork for parallel strategy execution.

```python
from finlab import data

# Temporarily run a strategy with a different date window and universe
with data.override(truncate_start='2020-01-01', truncate_end='2022-12-31'):
    with data.universe(market='TSE_OTC', category='半導體'):
        close = data.get('price:收盤價')
# Globals are automatically restored here

# The entire mutable data state is exposed as a `DataContext` object
ctx = data.DataContext.current()
```

Prefer `data.override()` / `data.universe()` over directly mutating module-level globals — mutations on the global `DataContext` are not thread-safe.

---

## Technical Indicators

Use `data.indicator()` to compute technical indicators using TA-Lib. Returns a FinLabDataFrame with the same structure as price data (date index, stock columns).

**Signature:**
```python
data.indicator(
    indname: str,
    adjust_price: bool = False,
    resample: str = 'D',
    **kwargs
) -> FinLabDataFrame | tuple
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `indname` | str | required | Indicator name: `SMA`, `EMA`, `RSI`, `MACD`, `STOCH`, `BBANDS`, `ATR`, `ADX`, etc. |
| `adjust_price` | bool | False | Use adjusted prices for calculation. |
| `resample` | str | 'D' | Data frequency: `'D'` (daily), `'W'` (weekly), `'M'` (monthly). |
| `**kwargs` | - | - | Indicator-specific parameters (e.g., `timeperiod`, `fastperiod`, `slowperiod`). |

**Returns:**
- Single indicator (SMA, RSI, etc.): `FinLabDataFrame`
- Multi-output indicator (STOCH, MACD, BBANDS): `tuple` of `FinLabDataFrame`

**Common Indicators:**

| Indicator | Parameters | Returns | Description |
|-----------|------------|---------|-------------|
| `SMA` | `timeperiod=30` | DataFrame | Simple Moving Average |
| `EMA` | `timeperiod=30` | DataFrame | Exponential Moving Average |
| `RSI` | `timeperiod=14` | DataFrame | Relative Strength Index (0-100) |
| `STOCH` | `fastk_period=5, slowk_period=3, slowd_period=3` | (k, d) tuple | Stochastic Oscillator |
| `MACD` | `fastperiod=12, slowperiod=26, signalperiod=9` | (macd, signal, hist) tuple | MACD |
| `BBANDS` | `timeperiod=5, nbdevup=2, nbdevdn=2` | (upper, middle, lower) tuple | Bollinger Bands |
| `ATR` | `timeperiod=14` | DataFrame | Average True Range |
| `ADX` | `timeperiod=14` | DataFrame | Average Directional Index |

**Examples:**
```python
from finlab import data

# Simple moving average
sma20 = data.indicator('SMA', timeperiod=20)
sma60 = data.indicator('SMA', timeperiod=60)

# RSI
rsi = data.indicator('RSI', timeperiod=14)
oversold = rsi < 30

# Stochastic oscillator (returns tuple)
k, d = data.indicator('STOCH', adjust_price=True)

# MACD (returns tuple)
macd, signal, hist = data.indicator('MACD')

# Bollinger Bands (returns tuple)
upper, middle, lower = data.indicator('BBANDS', timeperiod=20)

# Weekly RSI
rsi_weekly = data.indicator('RSI', timeperiod=14, resample='W')
```

---

## Universe Filtering

Limit the data fetch scope by market or industry category using a context manager or global settings.

### Supported Markets
- `ALL` - All markets
- `TSE` - Listed stocks (上市)
- `OTC` - Over-The-Counter (上櫃)
- `TSE_OTC` - Both TSE and OTC
- `ETF` - Exchange Traded Funds

### Supported Categories

**Industry Categories:**
光電業, 其他, 其他電子業, 化學工業, 半導體, 塑膠工業, 存託憑證, 建材營造, 文化創意業, 橡膠工業, 水泥工業, 汽車工業, 油電燃氣業, 玻璃陶瓷, 生技醫療, 生技醫療業, 紡織纖維, 航運業, 觀光事業, 貿易百貨, 資訊服務業, 農業科技, 通信網路業, 造紙工業, 金融, 鋼鐵工業, 電器電纜, 電子商務, 電子通路業, 電子零組件, 電機機械, 電腦及週邊, 食品工業

**ETF Categories:**
domestic_etf, foreign_etf, leveraged_etf, vanilla_futures_etf, leveraged_futures_etf

### Parameters

- `market` (str): One of 'ALL', 'TSE', 'OTC', 'TSE_OTC', 'ETF', plus `'TW_CB'` for Taiwan convertible bonds *(v1.5.13)*
- `category` (str or list): Industry NAMES only (no numeric codes); supports regex fuzzy match (e.g. '電子' matches multiple electronics categories)
- `exclude_category` (str or list or None): Excluded industry NAMES only (no numeric codes); same regex rules as category
- `index` (str or list, US only): *(v1.5.13)* Filter US stocks by market index — `'S&P 500'`, `'NASDAQ 100'`. Combinable with `sector`, `industry`, `exchange`. Use with `us_universe()` / `set_us_universe()`

### Important Notes

- Regex matching is used for categories. To match exact '其他', use '^其他$'
- When both category and exclude_category are provided, select category first, then subtract exclude_category
- Use data.universe ONLY to scope data.get() or backtest.sim() — do NOT wrap DataFrame/factor operations (e.g., position = ...)
- Do NOT use category codes (代號) like '28'; use industry names instead (e.g., exclude_category='金融')

### Examples

**Context Manager (Recommended):**
```python
from finlab import data

# Filter by market and category
with data.universe(market='TSE_OTC', category=['水泥工業']):
    price = data.get('price:收盤價')

# Exact match using regex
with data.universe(market='TSE_OTC', category=['^其他$']):
    close_subset = data.get('price:收盤價')

# Exclude specific categories
with data.universe(market='TSE_OTC', category=['水泥工業'], exclude_category=['金融']):
    price = data.get('price:收盤價')
```

**Global Setting:**
```python
from finlab import data

data.set_universe(market='TSE_OTC', category='水泥工業', exclude_category='金融')
price = data.get('price:收盤價')
```

**US market index filter** *(v1.5.13)*:
```python
from finlab import data

# S&P 500 constituents only
with data.us_universe(index='S&P 500'):
    adj_close = data.get('us_price:adj_close')

# NASDAQ 100 technology sector
with data.us_universe(index='NASDAQ 100', sector='Technology'):
    prices = data.get('us_price:adj_close')

# Globally scope US session
data.set_us_universe(index=['S&P 500', 'NASDAQ 100'])
```

---

## Data Catalog

### Price & Trading Data

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `price` | 上市櫃市場成交資訊 | 成交股數, 成交筆數, 成交金額, 收盤價, 開盤價, 最低價, 最高價, 最後揭示買價, 最後揭示賣價, 最後揭示買量, 最後揭示賣量 |
| `etl` | 還原權值股價 | adj_close, adj_open, adj_high, adj_low |
| `intraday_odd_lot_trade` | 上市櫃盤中零股成交資訊 | 成交股數, 成交筆數, 成交金額, 收盤價, 開盤價, 最低價, 最高價, 最後揭示買價, 最後揭示賣價, 最後揭示買量, 最後揭示賣量 |
| `after_market_odd_lot_trade` | 上市櫃盤後零股成交資訊 | 成交股數, 成交筆數, 成交金額, 成交價, 最後揭示買價, 最後揭示賣價, 最後揭示買量, 最後揭示賣量 |
| `intraday_trading` | 現股當沖成交資訊 | 當日沖銷交易成交股數, 當日沖銷交易買進成交金額, 當日沖銷交易賣出成交金額, 得先賣後買當沖 |
| `rotc_price` | 興櫃市場成交資訊 | 成交股數, 成交金額, 開盤價, 收盤價, 最高價, 最低價, 日均價, 成交筆數, 最後揭示買價, 最後揭示賣價 |

### Valuation Metrics

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `price_earning_ratio` | 個股日本益比、殖利率及股價淨值比 | 殖利率(%), 本益比, 股價淨值比 |
| `etl` | 個股市值 | market_value |

### Revenue Data

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `monthly_revenue` | 上市櫃月營收 | 當月營收, 上月營收, 去年當月營收, 上月比較增減(%), 去年同月增減(%), 當月累計營收, 去年累計營收, 前期比較增減(%) |
| `rotc_monthly_revenue` | 興櫃月營收 | 當月營收, 上月營收, 去年當月營收, 上月比較增減(%), 去年同月增減(%), 當月累計營收, 去年累計營收, 前期比較增減(%), 備註 |

### Financial Statements

The `financial_statement` table contains comprehensive balance sheet, income statement, and cash flow data with 100+ columns including:

**Balance Sheet Items:**
- Assets: 現金及約當現金, 流動資產, 非流動資產, 資產總額
- Liabilities: 流動負債, 非流動負債, 負債總額
- Equity: 股本, 資本公積合計, 保留盈餘, 股東權益總額

**Income Statement Items:**
- Revenue & Costs: 營業收入淨額, 營業成本, 營業毛利
- Expenses: 研究發展費, 推銷費用, 管理費用
- Profit: 營業利益, 稅前淨利, 歸屬母公司淨利(損), 每股盈餘

**Cash Flow Items:**
- Operating: 營業活動之淨現金流入(流出)
- Investing: 投資活動之淨現金流入(流出), 取得不動產_廠房及設備
- Financing: 籌資活動之淨現金流入(流出), 發放現金股利

### Fundamental Features

The `fundamental_features` table contains 50+ calculated financial metrics:

**Profitability Metrics:**
- ROA稅後息前, ROA綜合損益, ROE稅後, ROE綜合損益
- 營業毛利率, 營業利益率, 稅前淨利率, 稅後淨利率

**Growth Metrics:**
- 營收成長率, 營業毛利成長率, 營業利益成長率, 稅前淨利成長率, 稅後淨利成長率

**Efficiency Metrics:**
- 總資產週轉次數, 應收帳款週轉率, 存貨週轉率, 固定資產週轉次數

**Liquidity Metrics:**
- 流動比率, 速動比率, 現金流量比率

**Leverage Metrics:**
- 負債比率, 總負債除總淨值

**Per Share Metrics:**
- 每股營業額, 每股營業利益, 每股現金流量, 每股稅前淨利, 每股綜合損益, 每股稅後淨利

### Institutional Trading

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `institutional_investors_trading_summary` | 三大法人買賣超 | 外陸資買進股數(不含外資自營商), 外陸資賣出股數(不含外資自營商), 外陸資買賣超股數(不含外資自營商), 外資自營商買進股數, 外資自營商賣出股數, 外資自營商買賣超股數, 投信買進股數, 投信賣出股數, 投信買賣超股數, 自營商買進股數(自行買賣), 自營商賣出股數(自行買賣), 自營商買賣超股數(自行買賣), 自營商買進股數(避險), 自營商賣出股數(避險), 自營商買賣超股數(避險) |
| `foreign_investors_shareholding` | 外資持股比率 | 發行股數, 外資及陸資尚可投資股數, 全體外資及陸資持有股數, 外資及陸資尚可投資比率, 全體外資及陸資持股比率, 外資及陸資共用法令投資上限比率, 陸資法令投資上限比率 |

### Margin Trading

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `margin_transactions` | 融資券 | 融資買進, 融資賣出, 融資現金償還, 融資前日餘額, 融資今日餘額, 融資限額, 融券買進, 融券賣出, 融券現券償還, 融券前日餘額, 融券今日餘額, 融券限額, 資券互抵, 註記, 融資使用率, 融券使用率 |
| `security_lending` | 借券 | 前日借券餘額, 借券, 借券還券, 借券增減, 借券餘額 |
| `security_lending_sell` | 借券賣出 | 借券賣出, 借券賣出還券, 借券賣出餘額, 借券賣出限額 |

### Insider Trading

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `internal_equity_changes` | 內部人持股變化 | 發行股數, 董監增加股數, 董監減少股數, 董監持有股數, 董監持有股數占比, 經理人持有股數, 百分之十以上大股東持有股數, 市場別 |
| `internal_equity_pledge` | 內部人質押 | 董監持股, 董監設質, 董監解質, 董監累計設質, 董監設質股數占比, 經理人持股, 百分之十以上大股東持有股數, 經理人及百分之十以上大股東設質股數, 經理人及百分之十以上大股東設質股數占比, 市場別 |
| `inventory` | 集保餘額 | (Unstructured table - use directly) |

### Corporate Actions

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `dividend_tse` | 上市除權息 | 除權息前收盤價, 除權息參考價, 權值+息值, 權息, 漲停價格, 跌停價格, 開盤競價基準, 減除股利參考價, 詳細資料, 最近一次申報資料 季別日期, 最近一次申報每股 (單位)淨值, 最近一次申報每股 (單位)盈餘, twse_divide_ratio |
| `dividend_otc` | 上櫃除權息 | 除權息前收盤價, 除權息參考價, 權值, 息值, 權+息值, 權息, 漲停價格, 跌停價格, 開盤競價基準, 減除股利參考價, 現金股利, 每千股無償配股, 現金增資股數, 現金增資認購價, 公開承銷股數, 員工認購股數, 原股東認購數, 按持股比例千股認購, otc_divide_ratio |
| `capital_reduction_tse` | 上市減資 | 恢復買賣日期, 減資原因, 恢復買賣參考價, 停止買賣前收盤價格, 漲停價格, 跌停價格, 開盤競價基準, 除權參考價, twse_cap_divide_ratio |
| `capital_reduction_otc` | 上櫃減資 | 恢復買賣日期, 減資原因, 開始交易基準價, 最後交易之收盤價格, 減資恢復買賣開始日參考價格, 漲停價格, 跌停價格, 除權參考價, otc_cap_divide_ratio |
| `treasury_stock` | 庫藏股 | 買回目的, 買回股份總金額上限, 預定買回股數, 買回價格區間-最低, 買回價格區間-最高, 預定買回期間-起, 預定買回期間-迄, 是否執行完畢, 本次已買回股數, 本次執行完畢已註銷或轉讓股數, 本次已買回股數佔預定買回股數比例(%), 本次已買回總金額, 本次平均每股買回價格, 本次買回股數佔公司已發行股份總數比例(%), 本次未執行完畢之原因 |

### Market Indices

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `benchmark_return` | 回測基準 | 發行量加權股價報酬指數 |
| `taiex_total_index` | 發行量加權股價指數歷史資料 | 開盤指數, 最高指數, 最低指數, 收盤指數 |
| `stock_index_price` | 指數資訊 | 收盤指數, 漲跌百分比(%) |
| `stock_index_vol` | 指數成交量資訊 | 成交股數, 成交金額, 成交筆數 |
| `world_index` | 世界指數 | open, high, low, close, adj_close, volume |

### Economic Indicators

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `tw_business_indicators` | 景氣指標 | 景氣對策信號(分), 領先指標綜合指數(點), 領先指標不含趨勢指數(點), 同時指標綜合指數(點), 同時指標不含趨勢指數(點), 落後指標綜合指數(點), 落後指標不含趨勢指數(點) |
| `tw_total_pmi` | 製造業採購經理人指數 | 製造業PMI, 新增訂單數量, 生產數量, 人力僱用數量, 供應商交貨時間, 存貨, 客戶存貨, 原物料價格, 未完成訂單, 新增出口訂單, 進口原物料數量, 未來六個月展望 |
| `tw_total_nmi` | 非製造業採購經理人指數 | 臺灣非製造業NMI, 商業活動, 新增訂單, 人力僱用, 供應商交貨時間, 存貨, 採購價格, 未完成訂單, 服務輸出出口, 服務輸入進口, 服務收費價格, 存貨觀感, 未來六個月展望 |
| `tw_monetary_aggregates` | 貨幣總計數年增率 | 年增率(%) |

### Futures Data

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `futures_price` | 期貨日成交資訊 | 到期月份(週別), 開盤價, 最高價, 最低價, 收盤價, 漲跌價, 漲跌幅, 成交量, 未沖銷契約數 |
| `futures_institutional_investors_trading_summary` | 期貨三大法人盤後資訊 | 多方交易口數, 空方交易口數, 多空交易口數淨額, 多方未平倉口數, 空方未平倉口數, 多空未平倉口數淨額, 多方交易契約金額(千元), 空方交易契約金額(千元), 多空交易契約金額淨額(千元), 多方未平倉契約金額(千元), 空方未平倉契約金額(千元), 多空未平倉契約金額淨額(千元) |

### Convertible Bonds

| Table Name | Description | Available Columns |
|-----------|-------------|-------------------|
| `cb_price` | 可轉換公司債成交資訊 | 成交張數, 成交筆數, 成交金額, 收盤價, 開盤價, 最低價, 最高價 |
| `cb_converted_status` | 可轉換公司債每月轉換普通股 | 本月轉換張數, 轉(交)換或認股價格(元), 債券轉(交)換或認購普通股 |

### Company Information

| Table Name | Description |
|-----------|-------------|
| `company_basic_info` | 企業基本資訊 |
| `company_main_business` | 企業主要經營業務 |
| `important_subsidiary` | 企業重要子公司資訊 |
| `security_categories` | 證券分類 |
| `security_industry_themes` | 產業題材 |

**Stock ID to Name Mapping:**
```python
# company_basic_info 的 index 是流水號，需用 stock_id 欄位對應
info = data.get("company_basic_info")
name_map = dict(zip(info["stock_id"], info["公司簡稱"]))

# 用法: name_map.get("2330") -> "台積電"
df["股票名稱"] = df.index.map(lambda x: name_map.get(x, x))
```

### Special Status

| Table Name | Description | Usage |
|-----------|-------------|-------|
| `etl:disposal_stock_filter` | 排除處置股 | Boolean filter |
| `etl:noticed_stock_filter` | 排除注意股 | Boolean filter |
| `etl:full_cash_delivery_stock_filter` | 排除全額交割股 | Boolean filter |
| `trading_attention` | 注意股 | Status table |
| `disposal_information` | 處置股 | Status table |
| `change_transaction` | 上市櫃變更交易 | 變更交易, 分盤交易 |

### Special Dates

| Table Name | Description |
|-----------|-------------|
| `etl:financial_statements_deadline` | 財報截止日 |
| `etl:financial_statements_disclosure_dates` | 財報電子檔上傳日 |
| `financial_statements_upload_detail` | 財報電子檔上傳紀錄 |

---

## Plotting Data

Use `etl:adj_close` for historical comparison (backward adjusted, 向後還原).

```python
import matplotlib.pyplot as plt
from finlab import data, ffn_core

adj_close = data.get('etl:adj_close')
adj_close[['2330', '2317', '2454']].loc['2020':].rebase().plot(figsize=(12, 6))
plt.title('股價走勢比較')
plt.show()
```

---

## Storage Configuration

Control how data is cached locally. By default, FinLab caches data to disk to avoid repeated downloads.

### data.set_storage()

Configure the storage backend for data caching.

**Signature:**
```python
data.set_storage(storage: Storage) -> None
```

**Parameters:**
- `storage` (Storage, required): Storage backend instance. Options:
  - `data.FileStorage()` - Disk-based storage (default)
  - `data.CacheStorage()` - In-memory storage (faster, but lost on restart)

**Example:**
```python
from finlab import data

# Use in-memory storage (faster for repeated access in same session)
data.set_storage(data.CacheStorage())

# Use disk storage (default, persists across sessions)
data.set_storage(data.FileStorage())
```

### data.clear()

Clear all cached data from the current storage backend.

**Signature:**
```python
data.clear() -> None
```

**Example:**
```python
from finlab import data

# Clear all cached data
data.clear()

# Next data.get() will re-download from cloud
close = data.get('price:收盤價')
```

### Configuration Flags

Control data fetching behavior using module-level flags.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `data.use_local_data_only` | bool | False | Prevent cloud downloads; use only local cache. Raises error if data not cached. |
| `data.force_cloud_download` | bool | False | Always download fresh data from cloud, ignoring cache. |
| `data.prefer_local_if_exists` | bool | False | Use local cache without checking expiry. Faster startup. |
| `data.truncate_start` | str/None | None | Filter data to start from this date (format: `'YYYY-MM-DD'`). |
| `data.truncate_end` | str/None | None | Filter data to end at this date (format: `'YYYY-MM-DD'`). |

**Examples:**
```python
from finlab import data

# Offline mode - use only local cache
data.use_local_data_only = True
close = data.get('price:收盤價')  # Fails if not cached

# Force fresh download
data.force_cloud_download = True
close = data.get('price:收盤價')  # Always downloads

# Use local cache without expiry check (faster)
data.prefer_local_if_exists = True
close = data.get('price:收盤價')

# Limit data range
data.truncate_start = '2020-01-01'
data.truncate_end = '2023-12-31'
close = data.get('price:收盤價')  # Only 2020-2023 data

# Reset to defaults
data.use_local_data_only = False
data.force_cloud_download = False
data.prefer_local_if_exists = False
data.truncate_start = None
data.truncate_end = None
```

### Data Freshness Check

Verify cached data is up-to-date before executing trades.

```python
from finlab import data

# Check if all cached data is fresh (not expired, no pending crawl updates)
if data.is_tradable():
    print("Data is fresh — safe to trade")
else:
    print(f"Wait until: {data.suggested_tradable_time()}")

# Check next cache expiry time (UTC)
print(data.next_future_expiry())
```

| Function | Returns | Description |
|----------|---------|-------------|
| `data.is_tradable(market=None)` | `bool` | `True` when all cached data is not expired AND no more crawl updates expected before next market open |
| `data.suggested_tradable_time(market=None)` | `datetime\|None` | When `is_tradable()` will become `True`. `None` if already tradable |
| `data.next_future_expiry()` | `datetime\|None` | Next future expiry time (UTC) among cached datasets |

These are also available as Report methods: `report.is_tradable()`, `report.suggested_tradable_time()`, `report.next_future_expiry()`.

---

## Related References

- [FinlabDataFrame Reference](dataframe-reference.md) - Enhanced DataFrame methods for data manipulation
- [Backtesting Reference](backtesting-reference.md) - How to use data in backtesting
- [Factor Examples](factor-examples.md) - Practical examples using various datasets
- [Factor Analysis Reference](factor-analysis-reference.md) - Analyze factor effectiveness
