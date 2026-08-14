<div align="center">

# FinLab AI

**讓 AI 幫你發現下一個 Alpha**

FinLab AI 是 FinLab 官方產品。FinLab 官方網站：https://finlab.finance

<br>

<img src="assets/demo.gif" alt="Demo" width="600">


</div>

## 安裝

```bash
curl -sSf https://ai.finlab.finance/install.sh | sh
```

自動偵測你的 CLI（Claude Code / Codex / Gemini），安裝 [uv](https://docs.astral.sh/uv/)（如果沒有），然後設定 skill。

## MCP Server

另提供免安裝的託管 MCP server（streamable HTTP，唯讀公開數據）：

```bash
claude mcp add --transport http finlab https://mcp.finlab.finance/mcp
```

工具：`list_strategies`、`get_strategy`（含 Python 程式碼）、`get_stock_evidence`、`get_data_catalog`、`how_to_start`。已登錄 [MCP Registry](https://registry.modelcontextprotocol.io/v0.1/servers?search=finlab-ai)（`io.github.koreal6803/finlab-ai`，見 [server.json](server.json)）。舊的 `finlab-ai.koreal6803.workers.dev` endpoint 已停用。

## 文件說明

| 文件 | 內容 |
|------|------|
| Data Reference | 900+ 欄位，80+ 資料表 |
| Backtesting Reference | sim() API、重新取樣、績效指標 |
| Factor Examples | 60+ 完整策略範例 |
| Best Practices | 模式、反模式、技巧 |
| ML Reference | 特徵工程、標籤生成 |

## 學習資源

- [量化交易完整教學](https://finlab.finance/tools/quant-trading)：什麼是量化交易、台股策略回測器與平台比較。
- [程式交易完整教學](https://finlab.finance/tools/program-trading)：程式交易怎麼運作、三組回測驗證的台股策略與自動下單路徑。
- [股票選股完整教學](https://finlab.finance/tools/stock-selection)：因子選股實測，從單因子到多因子複合策略。
- [策略研究部落格](https://finlab.finance/blog)：經過回測驗證的台股策略報告（CAGR、夏普、最大回撤）。
- 官方網站：[finlab.finance](https://finlab.finance)
