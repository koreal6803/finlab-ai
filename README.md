# FinLab Claude Plugin

Claude Code skill for FinLab quantitative trading package, specifically designed for Taiwan stock market (台股) analysis.

## Features

- **Comprehensive Data Access**: Price data, financial statements, monthly revenue, valuation metrics, institutional trading
- **Strategy Development**: Factor-based strategy creation using FinLabDataFrame methods
- **Backtesting Engine**: Robust backtesting with risk management, stop-loss, take-profit
- **Factor Analysis**: IC calculation, Shapley values, centrality analysis
- **Machine Learning**: Feature engineering and label generation for trading models

## Installation

### Add the Marketplace

```bash
/plugin marketplace add <your-github-username>/finlab-claude-plugin
```

### Install the Plugin

```bash
/plugin install finlab-plugin@finlab-plugins
```

## Prerequisites

You need a FinLab API token to use this plugin. Get your token from: https://ai.finlab.tw/api_token/

Set the environment variable:
```bash
export FINLAB_API_TOKEN="your_token_here"
```

## Usage

Once installed, Claude Code will automatically use the FinLab skill when you:
- Ask about Taiwan stock market data
- Request trading strategy development
- Need backtesting analysis
- Work with FinLab-related code

## Example

```
User: "Show me the top 10 stocks with highest monthly revenue YOY growth"
Claude: [Uses FinLab skill to fetch and analyze data]
```

## Documentation

The plugin includes comprehensive reference documentation:
- Data catalog (900+ columns across 80+ tables)
- Backtesting API reference
- 60+ factor examples
- Best practices guide
- Machine learning reference

## License

MIT

## Author

FinLab Community
