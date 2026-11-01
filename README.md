<div align="center">

# FinLab AI

**Let AI discover your next alpha.**

FinLab AI is an official product of FinLab. FinLab official website: https://finlab.finance

Backtest Taiwan and U.S. stocks from Claude Code, Codex or Gemini CLI: your AI gets real market data and the FinLab backtest engine, with no scraping or backtest code of your own.

用 Claude Code、Codex 回測台股：AI 直接讀還原股價、月營收、財報、三大法人資料，用 FinLab 回測引擎驗證策略。

<br>

<img src="assets/demo.gif" alt="Demo" width="600">


</div>

## Installation

```bash
npx skills add koreal6803/finlab-ai --skill finlab -g -y
```

This installs the skill for Claude Code, Codex, Cursor and other tools that read Agent Skills, for every project on this machine. Or use your tool's own plugin command:

| Tool | Command |
|------|---------|
| Claude Code | `/plugin install finlab-plugin --marketplace koreal6803/finlab-ai` |
| Codex | `codex plugin marketplace add koreal6803/finlab-ai`, then `codex plugin add finlab-plugin@finlab-ai` |
| Cursor | **Customize** > **From GitHub Repository** > `koreal6803/finlab-ai` |

Then ask your AI: "Backtest a Taiwan stock strategy that buys the strongest monthly revenue growth." The first run asks you to sign in to FinLab once in your browser, which creates a free account with a 7-day full trial, no credit card needed.

### What it does on your machine

The skill is documentation: it has no hooks and no bundled programs. It tells your AI tool to install the `finlab` Python package with [uv](https://docs.astral.sh/uv/), sign in with `python -m finlab login`, which opens your browser, and download market data from FinLab. Strategy code runs on your machine, and nothing is uploaded unless you ask for it. It also documents broker order APIs, and tells your AI to show you a preview and wait for your confirmation before placing any real order.

## MCP Server

A hosted, read-only MCP server (streamable HTTP) is available — no install required:

```bash
claude mcp add --transport http finlab https://mcp.finlab.finance/mcp
```

Tools: `list_strategies`, `get_strategy` (with Python code), `get_stock_evidence`, `get_data_catalog`, `get_finlab_docs` (this skill's docs, always in sync with main), `how_to_start`. Listed on the [MCP Registry](https://registry.modelcontextprotocol.io/v0.1/servers?search=finlab-ai) as `io.github.koreal6803/finlab-ai` (see [server.json](server.json)). The old `finlab-ai.koreal6803.workers.dev` endpoint is retired.

## Documentation

| Document | Content |
|----------|---------|
| Data Reference | 900+ columns across 80+ tables |
| Backtesting Reference | sim() API, resampling, metrics |
| Factor Examples | 60+ complete strategy examples |
| Best Practices | Patterns, anti-patterns, tips |
| ML Reference | Feature engineering, labels |

## Learn more

- [Quant trading guide (量化交易)](https://finlab.finance/tools/quant-trading): what quantitative trading is, a Taiwan-stock strategy backtester, and a platform comparison.
- [Program trading guide (程式交易)](https://finlab.finance/tools/program-trading): how program trading works, three backtest-verified Taiwan-stock strategies, and an auto-trading walkthrough.
- [Stock selection guide (股票選股)](https://finlab.finance/tools/stock-selection): factor-based stock picking with real backtests, from single factors to multi-factor composites.
- [Strategy research blog](https://finlab.finance/blog): backtest-verified Taiwan-stock strategy reports (CAGR, Sharpe, max drawdown).
- Website: [finlab.finance](https://finlab.finance)
