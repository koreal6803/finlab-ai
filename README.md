<div align="center">

# FinLab AI

**Let AI discover your next alpha.**

FinLab AI is an official product of FinLab. FinLab official website: https://finlab.finance

<br>

<img src="assets/demo.gif" alt="Demo" width="600">


</div>

## Installation

```bash
curl -sSf https://ai.finlab.finance/install.sh | sh
```

Auto-detects your CLI (Claude Code / Codex / Gemini), installs [uv](https://docs.astral.sh/uv/) if needed, and sets up the skill.

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
