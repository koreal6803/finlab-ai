# Data Reference

## Overview

The FinLab data module provides comprehensive access to Taiwan stock market data, including prices, financial statements, fundamental metrics, institutional trading, and economic indicators. Use `data.get()` to retrieve any dataset using a simple path-based syntax.

---

## Usage

### Basic Syntax

```python
from finlab import data

# Retrieve data using TABLE:COLUMN format
df = data.get('price:收盤價')

# For tables without columns, use TABLE directly
inventory = data.get('inventory')
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
eps = data.get('fundamental_features:每股盈餘')

# Get foreign investor trading volume
foreign_investment = data.get('institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)')
```

### Common Field Names

| Term | Field |
|------|-------|
| EPS | `fundamental_features:每股稅後盈餘` |
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

```python
data.search(keyword: str = None) -> list
```

| Parameter | Description |
|-----------|-------------|
| `keyword` | Optional. Filter datasets by keyword (case-insensitive substring match). Returns all if omitted. |

**Returns:** List of `"table:column"` strings, usable directly with `data.get()`.

**Examples:**
```python
from finlab import data

# List all available datasets
all_data = data.search()

# Search by keyword
data.search('收盤')    # ['price:收盤價']
data.search('營收')    # ['monthly_revenue:當月營收', ...]

# Use result with data.get()
results = data.search('收盤')
df = data.get(results[0])
```

---

## Universe Filtering

Limit the data fetch scope by market or industry category using a context manager or global settings.

### Supported Markets
- `ALL` - All markets
- `TSE` - Taiwan Stock Exchange (上市)
- `OTC` - Over-The-Counter (上櫃)
- `TSE_OTC` - Both TSE and OTC
- `ETF` - Exchange Traded Funds

### Supported Categories

**Industry Categories:**
光電業, 其他, 其他電子業, 化學工業, 半導體, 塑膠工業, 存託憑證, 建材營造, 文化創意業, 橡膠工業, 水泥工業, 汽車工業, 油電燃氣業, 玻璃陶瓷, 生技醫療, 生技醫療業, 紡織纖維, 航運業, 觀光事業, 貿易百貨, 資訊服務業, 農業科技, 通信網路業, 造紙工業, 金融, 鋼鐵工業, 電器電纜, 電子商務, 電子通路業, 電子零組件, 電機機械, 電腦及週邊, 食品工業

**ETF Categories:**
domestic_etf, foreign_etf, leveraged_etf, vanilla_futures_etf, leveraged_futures_etf

### Parameters

- `market` (str): One of 'ALL', 'TSE', 'OTC', 'TSE_OTC', 'ETF'
- `category` (str or list): Industry NAMES only (no numeric codes); supports regex fuzzy match (e.g. '電子' matches multiple electronics categories)
- `exclude_category` (str or list or None): Excluded industry NAMES only (no numeric codes); same regex rules as category

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
| `tw_business_indicators` | 台灣景氣指標 | 景氣對策信號(分), 領先指標綜合指數(點), 領先指標不含趨勢指數(點), 同時指標綜合指數(點), 同時指標不含趨勢指數(點), 落後指標綜合指數(點), 落後指標不含趨勢指數(點) |
| `tw_total_pmi` | 台灣製造業採購經理人指數 | 製造業PMI, 新增訂單數量, 生產數量, 人力僱用數量, 供應商交貨時間, 存貨, 客戶存貨, 原物料價格, 未完成訂單, 新增出口訂單, 進口原物料數量, 未來六個月展望 |
| `tw_total_nmi` | 台灣非製造業採購經理人指數 | 臺灣非製造業NMI, 商業活動, 新增訂單, 人力僱用, 供應商交貨時間, 存貨, 採購價格, 未完成訂單, 服務輸出出口, 服務輸入進口, 服務收費價格, 存貨觀感, 未來六個月展望 |
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
| `security_categories` | 台股證券分類 |
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

## Related References

- [FinlabDataFrame Reference](dataframe-reference.md) - Enhanced DataFrame methods for data manipulation
- [Backtesting Reference](backtesting-reference.md) - How to use data in backtesting
- [Factor Examples](factor-examples.md) - Practical examples using various datasets
- [Factor Analysis Reference](factor-analysis-reference.md) - Analyze factor effectiveness
