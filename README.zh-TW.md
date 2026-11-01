<div align="center">

# FinLab AI

**讓 AI 幫你發現下一個 Alpha**

FinLab AI 是 FinLab 官方產品。FinLab 官方網站：https://finlab.finance

<br>

<img src="assets/demo.gif" alt="Demo" width="600">


</div>

## 安裝

```bash
npx skills add koreal6803/finlab-ai --skill finlab -g -y
```

這一行會把 skill 裝給 Claude Code、Codex、Cursor 與其他讀 Agent Skills 的工具，這台電腦的每個專案都用得到。也可以用工具自己的外掛指令：

| 工具 | 指令 |
|------|------|
| Claude Code | `/plugin install finlab-plugin --marketplace koreal6803/finlab-ai` |
| Codex | `codex plugin marketplace add koreal6803/finlab-ai`，再 `codex plugin add finlab-plugin@finlab-ai` |
| Cursor | **Customize** > **From GitHub Repository** > `koreal6803/finlab-ai` |

接著問你的 AI：「幫我回測月營收成長最強的台股策略」。第一次會請你在瀏覽器登入 FinLab 一次，自動建立免費帳號，含 7 天完整試用，不用信用卡。

### 在你的電腦上會做什麼

skill 本身是文件，沒有 hook，也沒有內附程式。它會請 AI 工具用 [uv](https://docs.astral.sh/uv/) 安裝 `finlab` Python 套件、執行 `python -m finlab login`（開瀏覽器登入），再從 FinLab 下載市場資料。策略程式在你的電腦上執行，沒有你的要求不會上傳任何東西。skill 也包含券商下單 API 的說明，並要求 AI 先給你看預覽，等你確認才下真實訂單。

## MCP Server

另提供免安裝的託管 MCP server（streamable HTTP，唯讀公開數據）：

```bash
claude mcp add --transport http finlab https://mcp.finlab.finance/mcp
```

工具：`list_strategies`、`get_strategy`（含 Python 程式碼）、`get_stock_evidence`、`get_data_catalog`、`get_finlab_docs`（本 skill 文件，與 main 分支即時同步）、`how_to_start`。已登錄 [MCP Registry](https://registry.modelcontextprotocol.io/v0.1/servers?search=finlab-ai)（`io.github.koreal6803/finlab-ai`，見 [server.json](server.json)）。舊的 `finlab-ai.koreal6803.workers.dev` endpoint 已停用。

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
