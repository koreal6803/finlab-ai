# Factor Analysis Reference

## Overview

The FinLab factor analysis module provides comprehensive tools for evaluating factor effectiveness, calculating Information Coefficient (IC), analyzing factor trends, and computing factor contributions using Shapley values. These tools help you understand which factors drive returns and how to construct better trading strategies.

**Import:**
```python
from finlab.tools.factor_analysis import (
    generate_features_and_labels,
    calc_factor_return,
    calc_ic,
    ic,
    calc_metric,
    calc_shapley_values,
    calc_centrality,
    calc_regression_stats
)
```

---

## Quick Start

### Basic Factor Analysis Workflow

```python
from finlab import data
from finlab.tools.factor_analysis import generate_features_and_labels, calc_factor_return, calc_ic

# Get data
price = data.get('etl:adj_close')
marketcap = data.get('etl:market_value')
revenue = data.get('monthly_revenue:當月營收')

# Generate features and labels
features, labels = generate_features_and_labels({
    'marketcap': marketcap.rank(pct=True, axis=1) < 0.3,
    'revenue': (revenue.average(3) / revenue.average(12)).rank(pct=True, axis=1) < 0.3,
    'momentum': price / price.shift(20) - 1 > 0,
}, resample=revenue.index)

# Calculate factor returns
factor_return = calc_factor_return(features, labels)
print(factor_return.head())

# Calculate IC (Information Coefficient)
ic_df = calc_ic(features, labels, rank=True)
print(ic_df.mean())
```

---

## Functions

### generate_features_and_labels

Generate factor features and labels: combines factors into a feature DataFrame and generates excess return labels.

**Signature:**
```python
generate_features_and_labels(
    dfs: Dict[str, Union[pd.DataFrame, Callable]],
    resample: str
) -> tuple[pd.DataFrame, pd.Series]
```

**Parameters:**
- `dfs` (dict, required): Factor dictionary where keys are factor names and values are DataFrame or callable functions that return DataFrame (standard input for feature.combine)
- `resample` (str, required): Resampling frequency string (e.g., 'M', 'Q', 'Y'), used for feature and label generation

**Returns:**
- `tuple[pd.DataFrame, pd.Series]`: (features, labels). features has date index with columns as factor names; labels are excess returns with the same index

**Example:**
```python
from finlab import data
from finlab.tools.factor_analysis import generate_features_and_labels

price = data.get('etl:adj_close')
marketcap = data.get('etl:market_value')
revenue = data.get('monthly_revenue:當月營收')

features, labels = generate_features_and_labels({
    'marketcap': marketcap.rank(pct=True, axis=1) < 0.3,
    'revenue': (revenue.average(3) / revenue.average(12)).rank(pct=True, axis=1) < 0.3,
    'momentum': price / price.shift(20) - 1 > 0,
}, resample=revenue.index)

print(f'Features shape: {features.shape}')
print(f'Labels shape: {labels.shape}')
```

---

### calc_factor_return

Calculate equal-weight portfolio returns based on features and labels. Automatically validates features as boolean values, calculates equal-weight portfolio returns per factor, and outputs starting from the first non-empty row.

**Signature:**
```python
calc_factor_return(
    features: pd.DataFrame,
    labels: pd.Series
) -> pd.DataFrame
```

**Parameters:**
- `features` (pd.DataFrame, required): Feature DataFrame with date index, factor names as columns, and boolean values
- `labels` (pd.Series, required): Label Series with date index and excess returns as values

**Returns:**
- `pd.DataFrame`: Equal-weight portfolio period returns indexed by date with factor names as columns, starting from the first non-empty row

**Example:**
```python
from finlab import data
from finlab.tools.factor_analysis import calc_factor_return, generate_features_and_labels

price = data.get('etl:adj_close')
marketcap = data.get('etl:market_value')
revenue = data.get('monthly_revenue:當月營收')

# Generate features and labels
features, labels = generate_features_and_labels({
    'marketcap': marketcap.rank(pct=True, axis=1) < 0.3,
    'revenue': (revenue.average(3) / revenue.average(12)).rank(pct=True, axis=1) < 0.3,
    'momentum': price / price.shift(20) - 1 > 0,
}, resample=revenue.index)

# Calculate factor returns
factor_return = calc_factor_return(features, labels)
print(factor_return.head())

# Analyze cumulative returns
cumulative_return = (1 + factor_return).cumprod()
cumulative_return.plot(figsize=(12, 6))
```

---

### calc_ic

Calculate the correlation coefficient (IC) between features and labels. Optionally rank features first for Rank IC. Outputs starting from the first non-empty row.

**Signature:**
```python
calc_ic(
    features: pd.DataFrame,
    labels: pd.Series,
    rank: bool = False
) -> pd.DataFrame
```

**Parameters:**
- `features` (pd.DataFrame, required): Feature DataFrame with MultiIndex (date, stock_id) and factor names as columns
- `labels` (pd.Series, required): Label Series with MultiIndex (date, stock_id)
- `rank` (bool, optional, default=False): Whether to rank features first for calculating Rank IC

**Returns:**
- `pd.DataFrame`: IC values for each date and factor, starting from the first non-empty row

**Example:**
```python
from finlab import data
from finlab.tools.factor_analysis import calc_ic, generate_features_and_labels

price = data.get('etl:adj_close')
marketcap = data.get('etl:market_value')
revenue = data.get('monthly_revenue:當月營收')

# Generate features and labels (MultiIndex: date, stock_id)
features, labels = generate_features_and_labels({
    'marketcap': marketcap.rank(pct=True, axis=1) < 0.3,
    'revenue': (revenue.average(3) / revenue.average(12)).rank(pct=True, axis=1) < 0.3,
    'momentum': price / price.shift(20) - 1 > 0,
}, resample=revenue.index)

# Calculate Rank IC
ic_df = calc_ic(features, labels, rank=True)
print(ic_df.head())

# Analyze IC statistics
print(ic_df.mean())  # Mean IC
print(ic_df.std())   # IC volatility
print(ic_df.mean() / ic_df.std())  # IC IR (Information Ratio)
```

---

### ic

Calculate Information Coefficient (IC) for factors. Internally calls calc_metric with cross-sectional correlation as the evaluation function.

**Signature:**
```python
ic(
    factor: pd.DataFrame | Dict[str, pd.DataFrame],
    adj_close: pd.DataFrame,
    days: list[int] = [10, 20, 60, 120]
) -> pd.DataFrame
```

**Parameters:**
- `factor` (pd.DataFrame or dict, required): Factor data as DataFrame (columns are stock IDs) or dict[str, DataFrame] (keys are factor names)
- `adj_close` (pd.DataFrame, required): Adjusted closing price DataFrame (columns are stock IDs) for calculating future returns
- `days` (list[int], optional, default=[10, 20, 60, 120]): Prediction horizon list for calculating d-day future returns

**Returns:**
- `pd.DataFrame`: IC for each factor at different prediction horizons. Column names are <factor>_<days>, indexed by date

**Example:**
```python
from finlab import data
from finlab.tools.factor_analysis import ic

# Build factor and price
factor = data.indicator('RSI')
adj_close = data.get('etl:adj_close')

# Calculate IC (correlation coefficient)
ic_df = ic(factor, adj_close)
print(ic_df.head())

# Analyze IC at different horizons
print(ic_df.mean())
ic_df.plot(figsize=(12, 6))
```

---

### calc_metric

Calculate evaluation metrics for factors and future returns at multiple prediction horizons. Supports single DataFrame or mapping of factor names to DataFrames. Automatically aligns and trims time series.

**Signature:**
```python
calc_metric(
    factor: pd.DataFrame | Dict[str, pd.DataFrame],
    adj_close: pd.DataFrame,
    days: list[int] = [10, 20, 60, 120],
    func = corr
) -> pd.DataFrame
```

**Parameters:**
- `factor` (pd.DataFrame or dict, required): Factor data as DataFrame (columns are stock IDs) or dict[str, DataFrame] (keys are factor names)
- `adj_close` (pd.DataFrame, required): Adjusted closing price DataFrame (columns are stock IDs) for calculating future returns
- `days` (list[int], optional, default=[10, 20, 60, 120]): Prediction horizon list for calculating d-day future returns
- `func` (callable, optional): Aggregation function for each date group. Takes DataFrame with 'ret' and 'f' columns and returns a single statistic. Default is corr (correlation coefficient)

**Returns:**
- `pd.DataFrame`: Evaluation results for each factor at different prediction horizons. Column names are <factor>_<days>, indexed by date

**Example:**
```python
from finlab import data
from finlab.tools.factor_analysis import calc_metric

# Build factor and price
factor = data.indicator('RSI')
adj_close = data.get('etl:adj_close')

# Calculate evaluation metric (default: correlation coefficient)
metric_df = calc_metric(factor, adj_close)
print(metric_df.head())

# Use custom metric function
def custom_metric(df):
    # Calculate Spearman correlation
    return df['f'].corr(df['ret'], method='spearman')

metric_df = calc_metric(factor, adj_close, func=custom_metric)
```

---

### calc_shapley_values

Calculate Shapley values for each factor to measure marginal contribution to portfolio performance using cooperative game theory. Enumerates all factor subsets and averages marginal contributions. Computational complexity is O(2^n) where n is the number of factors.

**Signature:**
```python
calc_shapley_values(
    features: pd.DataFrame,
    labels: pd.Series
) -> pd.DataFrame
```

**Parameters:**
- `features` (pd.DataFrame, required): Feature DataFrame with date index, factor names as columns, and boolean values (True indicates selected)
- `labels` (pd.Series, required): Label Series with MultiIndex ('datetime', 'stock_id') and excess returns as values

**Returns:**
- `pd.DataFrame`: Daily Shapley values for each factor. Indexed by date with factor names as columns

**Example:**
```python
from finlab import data
from finlab.tools.factor_analysis import calc_shapley_values, generate_features_and_labels

price = data.get('etl:adj_close')
marketcap = data.get('etl:market_value')
revenue = data.get('monthly_revenue:當月營收')

# Generate features and labels
features, labels = generate_features_and_labels({
    'marketcap': marketcap.rank(pct=True, axis=1) < 0.3,
    'revenue': (revenue.average(3) / revenue.average(12)).rank(pct=True, axis=1) < 0.3,
    'momentum': price / price.shift(20) - 1 > 0,
}, resample=revenue.index)

# Calculate Shapley values
shapley_df = calc_shapley_values(features, labels)
print(shapley_df.head())

# Analyze average contribution
print(shapley_df.mean())
shapley_df.plot(figsize=(12, 6))
```

**Note:** Due to computational complexity, this function is best used with a small number of factors (typically < 10).

---

### calc_centrality

Calculate rolling asset centrality for time series data. This is a generic function applicable to any DataFrame with time index and asset columns (e.g., factor returns). It is frequency-agnostic with rolling window specified by integer window_periods.

**Signature:**
```python
calc_centrality(
    return_df: pd.DataFrame,
    window_periods: int,
    n_components: int = 1
) -> pd.DataFrame
```

**Parameters:**
- `return_df` (pd.DataFrame, required): Time series DataFrame indexed by date with assets (e.g., factor names) as columns. Despite the name return_df, it can be any asset time series
- `window_periods` (int, required): Rolling window length in number of data points. For monthly data, 3 means 3 months
- `n_components` (int, optional, default=1): Number of principal components for PCA calculation

**Returns:**
- `pd.DataFrame`: DataFrame with rolling centrality scores. Indexed by date (window end date) with assets as columns

**Example:**
```python
import pandas as pd
from finlab.tools.factor_analysis import calc_centrality

# Assume we have factor return time series data
data = {
    'FactorA': [0.1, 0.2, 0.15, 0.12, 0.11],
    'FactorB': [0.05, 0.04, 0.06, 0.07, 0.08],
}
index = pd.to_datetime(['2025-01-01','2025-01-02','2025-01-03','2025-01-04','2025-01-05'])
return_df = pd.DataFrame(data, index=index)

centrality_df = calc_centrality(return_df, window_periods=3, n_components=1)
print(centrality_df.head())
```

---

### calc_regression_stats

Perform linear regression on each time series in a DataFrame and return statistics (slope, p-value, R², tail estimate, and trend classification). Uses vectorized implementation without SciPy dependency.

**Signature:**
```python
calc_regression_stats(
    df: pd.DataFrame,
    p_value_threshold: float = 0.05,
    r_squared_threshold: float = 0.1
) -> pd.DataFrame
```

**Parameters:**
- `df` (pd.DataFrame, required): Time series DataFrame indexed by DatetimeIndex with different metrics as columns
- `p_value_threshold` (float, optional, default=0.05): P-value threshold for trend significance
- `r_squared_threshold` (float, optional, default=0.1): R² threshold for trend explanatory power

**Returns:**
- `pd.DataFrame`: Regression statistics for each column including slope, p_value, r_squared, tail_estimate, and trend

**Example:**
```python
# Assume ic_df is a time series of factor IC
from finlab.tools.factor_analysis import calc_regression_stats

trend_stats = calc_regression_stats(ic_df)
print(trend_stats.head())

# Filter for statistically significant upward trends
significant_up = trend_stats[(trend_stats['p_value'] < 0.05) & (trend_stats['slope'] > 0)]
print(significant_up)
```

---

## Advanced Analysis Examples

### Complete Factor Analysis Pipeline

```python
from finlab import data
from finlab.tools.factor_analysis import (
    generate_features_and_labels,
    calc_factor_return,
    calc_ic,
    calc_regression_stats,
    calc_shapley_values
)
import matplotlib.pyplot as plt

# 1. Define factors
price = data.get('etl:adj_close')
marketcap = data.get('etl:market_value')
revenue = data.get('monthly_revenue:當月營收')
pb = data.get('price_earning_ratio:股價淨值比')

# 2. Generate features and labels
features, labels = generate_features_and_labels({
    'small_cap': marketcap.rank(pct=True, axis=1) < 0.3,
    'revenue_growth': (revenue.average(3) / revenue.average(12)).rank(pct=True, axis=1) < 0.3,
    'momentum': price / price.shift(20) - 1 > 0,
    'low_pb': pb.rank(pct=True, axis=1) < 0.3,
}, resample='M')

# 3. Calculate factor returns
factor_return = calc_factor_return(features, labels)
cumulative_return = (1 + factor_return).cumprod()

# 4. Calculate IC
ic_df = calc_ic(features, labels, rank=True)
print("Average IC:")
print(ic_df.mean())

# 5. Analyze IC trends
ic_trends = calc_regression_stats(ic_df)
print("\nIC Trend Statistics:")
print(ic_trends)

# 6. Calculate Shapley values (factor contributions)
shapley_df = calc_shapley_values(features, labels)
print("\nAverage Shapley Values:")
print(shapley_df.mean())

# 7. Visualization
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# Plot cumulative returns
cumulative_return.plot(ax=axes[0])
axes[0].set_title('Cumulative Factor Returns')
axes[0].set_ylabel('Cumulative Return')
axes[0].grid(True)

# Plot IC over time
ic_df.plot(ax=axes[1])
axes[1].set_title('Information Coefficient (IC) Over Time')
axes[1].set_ylabel('IC')
axes[1].axhline(y=0, color='r', linestyle='--', alpha=0.3)
axes[1].grid(True)

# Plot Shapley values
shapley_df.plot(ax=axes[2])
axes[2].set_title('Shapley Values (Factor Contributions)')
axes[2].set_ylabel('Shapley Value')
axes[2].grid(True)

plt.tight_layout()
plt.show()
```

---

### Multi-Horizon IC Analysis

```python
from finlab import data
from finlab.tools.factor_analysis import ic
import matplotlib.pyplot as plt

# Calculate factor
rsi = data.indicator('RSI')
adj_close = data.get('etl:adj_close')

# Calculate IC at multiple horizons
ic_df = ic(rsi, adj_close, days=[5, 10, 20, 40, 60, 120])

# Analyze IC statistics
print("IC Mean:")
print(ic_df.mean())
print("\nIC Std:")
print(ic_df.std())
print("\nIC IR (Mean/Std):")
print(ic_df.mean() / ic_df.std())

# Visualization
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# IC time series
ic_df.plot(ax=axes[0])
axes[0].set_title('IC Across Different Horizons')
axes[0].set_ylabel('IC')
axes[0].axhline(y=0, color='r', linestyle='--', alpha=0.3)
axes[0].grid(True)

# IC distribution
ic_df.plot(kind='box', ax=axes[1])
axes[1].set_title('IC Distribution Across Horizons')
axes[1].set_ylabel('IC')
axes[1].grid(True)

plt.tight_layout()
plt.show()
```

---

### Factor Combination Analysis

```python
from finlab import data
from finlab.tools.factor_analysis import (
    generate_features_and_labels,
    calc_factor_return
)
import pandas as pd

# Define multiple factors
price = data.get('etl:adj_close')
marketcap = data.get('etl:market_value')
revenue = data.get('monthly_revenue:當月營收')

# Generate individual features
individual_features, labels = generate_features_and_labels({
    'small_cap': marketcap.rank(pct=True, axis=1) < 0.3,
    'revenue_growth': (revenue.average(3) / revenue.average(12)).rank(pct=True, axis=1) < 0.3,
    'momentum': price / price.shift(20) - 1 > 0,
}, resample='M')

# Create combined features
combined_features = pd.DataFrame(index=individual_features.index)
combined_features['small_cap'] = individual_features['small_cap']
combined_features['revenue_growth'] = individual_features['revenue_growth']
combined_features['momentum'] = individual_features['momentum']
combined_features['small_cap+revenue'] = individual_features['small_cap'] & individual_features['revenue_growth']
combined_features['all_three'] = individual_features['small_cap'] & individual_features['revenue_growth'] & individual_features['momentum']

# Calculate returns for all combinations
factor_return = calc_factor_return(combined_features, labels)
cumulative_return = (1 + factor_return).cumprod()

# Compare performance
print("Cumulative Return (Final):")
print(cumulative_return.iloc[-1])

print("\nAnnualized Return:")
print(factor_return.mean() * 12)

print("\nAnnualized Volatility:")
print(factor_return.std() * (12 ** 0.5))

print("\nSharpe Ratio:")
print((factor_return.mean() / factor_return.std()) * (12 ** 0.5))

# Visualization
cumulative_return.plot(figsize=(14, 6))
plt.title('Factor Combination Performance Comparison')
plt.ylabel('Cumulative Return')
plt.grid(True)
plt.show()
```

---

## Best Practices

1. **Use Rank IC for robustness** - Rank IC is more stable than raw IC
2. **Analyze IC over time** - Look for consistent positive IC, not just average IC
3. **Check IC trend** - Use calc_regression_stats to identify deteriorating factors
4. **Calculate Shapley values** - Understand true factor contributions in multi-factor strategies
5. **Test multiple horizons** - Different factors may work at different time scales
6. **Combine complementary factors** - Factors with low correlation often work better together
7. **Monitor factor centrality** - High centrality may indicate overcrowding
8. **Validate out-of-sample** - Always test on unseen data periods

---

## Related References

- [FinlabDataFrame Reference](dataframe-reference.md) - Enhanced DataFrame methods
- [Data Reference](data-reference.md) - Available data sources
- [Factor Examples](factor-examples.md) - Practical factor calculations
- [Machine Learning Reference](machine-learning-reference.md) - ML-based factor analysis
- [Backtesting Reference](backtesting-reference.md) - Test factor-based strategies
