# Trading & Order Execution Reference

## Overview

This reference covers the complete workflow for executing trades from backtest results to live orders. The process involves:

1. **Position Calculation**: Convert backtest results to lot (張) quantities
2. **Broker Connection**: Configure and connect to your broker account
3. **Order Execution**: Create, update, and manage orders via OrderExecutor
4. **Realtime Sync** *(v2.0.0)*: Subscribe to live position/fill streams via `PositionStreamMixin`

---

## Typed Data Contracts — `finlab.schemas`

*(v1.5.9)* `finlab.schemas` exposes formal dataclass / TypedDict contracts used across the trading stack. Prefer these over untyped dict access when writing production integrations — the types are enforced at boundaries (`PortfolioSyncManager`, `OrderExecutor`) and catch schema drift at code-review time.

```python
from finlab.schemas import (
    PositionEntry,   # one holding line: symbol, quantity, order_condition, weight
    OrderEntry,      # one planned order: symbol, quantity, order_condition
    PortfolioData,   # full portfolio snapshot consumed by PortfolioSyncManager
)
```

**Deprecation note:** `symbol` is the canonical field — see `docs/details/typed_data_interfaces.md` in the finlab repo. `stock_id` is still accepted as an alias in dict payloads (`Position` entries, `from_dict()` input), but on the dataclasses `entry.stock_id` raises `AttributeError`.

---

## Position Class

The `Position` class represents target holdings and provides methods for converting backtest results to executable positions.

`quantity` is in board lots (張), not shares: one Taiwan lot is 1,000 shares, so `{'2330': 1}` is 1,000 shares and `1.001` is 1 lot + 1 odd-lot share. Negative quantities are short positions.

**Import:**
```python
from finlab.online.order_executor import Position
```

### Position.from_report()

Convert a backtest report to tradeable positions.

**Signature:**
```python
Position.from_report(
    report,
    fund: float,
    odd_lot: bool = False
) -> Position
```

**Parameters:**
- `report` (Report, required): Backtest report object from `sim()`
- `fund` (float, required): Total capital for position sizing (in the broker's account currency)
- `odd_lot` (bool, default=False): Enable odd lot (零股) trading for smaller positions

**Returns:**
- `Position`: Target holdings, one entry per stock; `quantity` is in lots (see [Position Class](#position-class))

**Example:**
```python
from finlab import backtest
from finlab.online.order_executor import Position

report = backtest.sim(position, resample="M")

# Standard lot trading
position = Position.from_report(report, fund=1000000)
print(position)
# symbol stock_id  quantity order_condition  weight
#   2330     2330         1            CASH     0.1

entries = position.position  # list of entry dicts, one per stock

# Odd lot trading (smaller positions)
position = Position.from_report(report, fund=1000000, odd_lot=True)
```

---

### Custom Position

Create a position manually without backtest.

**Signature:**
```python
Position(stocks: dict[str, float]) -> Position
```

**Example:**
```python
# 1 lot of 2330 and 2 lots of 1101
position = Position({'2330': 1, '1101': 2})

# Odd lots: 1 lot + 1 share of 1101
position = Position({'2330': 1, '1101': 1.001})
```

---

### Position Arithmetic

Combine or modify positions using arithmetic operations.

**Subtraction:**
```python
# Remove stocks from position
new_position = position - Position({'2330': 1})
```

**Addition:**
```python
# Add stocks to position
new_position = position + Position({'1101': 1})
```

**Multi-strategy combination:**
```python
# Combine positions from multiple strategies
position1 = Position.from_report(report1, fund=500000)
position2 = Position.from_report(report2, fund=500000)
total_position = position1 + position2
```

---

## Broker Account Setup

### Environment Variables Summary

| Broker | Required Environment Variables |
|--------|-------------------------------|
| Esun (玉山) | `ESUN_CONFIG_PATH`, `ESUN_MARKET_API_KEY`, `ESUN_ACCOUNT_PASSWORD`, `ESUN_CERT_PASSWORD` |
| Sinopac (永豐) | `SHIOAJI_API_KEY`, `SHIOAJI_SECRET_KEY`, `SHIOAJI_CERT_PERSON_ID`, `SHIOAJI_CERT_PATH`, `SHIOAJI_CERT_PASSWORD` |
| Masterlink (元富) | `MASTERLINK_NATIONAL_ID`, `MASTERLINK_ACCOUNT`, `MASTERLINK_ACCOUNT_PASS`, `MASTERLINK_CERT_PATH`, `MASTERLINK_CERT_PASS` |
| Fubon (富邦) | `FUBON_NATIONAL_ID`, `FUBON_ACCOUNT_PASS`, `FUBON_CERT_PATH` |

---

### Esun (玉山證券)

**Import:**
```python
from finlab.online.esun_account import EsunAccount
```

**Environment Variables:**
```bash
export ESUN_CONFIG_PATH='/path/to/config.ini'
export ESUN_MARKET_API_KEY='your_market_api_key'
export ESUN_ACCOUNT_PASSWORD='your_password'
export ESUN_CERT_PASSWORD='your_cert_password'
```

**Usage:**
```python
import os

os.environ['ESUN_CONFIG_PATH'] = '/path/to/config.ini'
os.environ['ESUN_MARKET_API_KEY'] = 'your_market_api_key'
os.environ['ESUN_ACCOUNT_PASSWORD'] = 'your_password'
os.environ['ESUN_CERT_PASSWORD'] = 'your_cert_password'

acc = EsunAccount()
```

**Install SDK:**
```bash
pip install esun-trade
```

---

### Sinopac (永豐證券)

**Import:**
```python
from finlab.online.sinopac_account import SinopacAccount
```

**Environment Variables:**
```bash
export SHIOAJI_API_KEY='api_key'
export SHIOAJI_SECRET_KEY='secret_key'
export SHIOAJI_CERT_PERSON_ID='A123456789'
export SHIOAJI_CERT_PATH='/path/to/cert'
export SHIOAJI_CERT_PASSWORD='cert_password'
```

**Usage:**
```python
import os

os.environ['SHIOAJI_API_KEY'] = 'api_key'
os.environ['SHIOAJI_SECRET_KEY'] = 'secret_key'
os.environ['SHIOAJI_CERT_PERSON_ID'] = 'A123456789'
os.environ['SHIOAJI_CERT_PATH'] = '/path/to/cert'
os.environ['SHIOAJI_CERT_PASSWORD'] = 'cert_password'

acc = SinopacAccount()
```

**Install SDK:**
```bash
pip install shioaji
```

---

### Masterlink (元富證券)

**Import:**
```python
from finlab.online.masterlink_account import MasterlinkAccount
```

**Environment Variables:**
```bash
export MASTERLINK_NATIONAL_ID='A123456789'
export MASTERLINK_ACCOUNT='account'
export MASTERLINK_ACCOUNT_PASS='password'
export MASTERLINK_CERT_PATH='/path/to/cert'
export MASTERLINK_CERT_PASS='cert_password'
```

**Usage:**
```python
import os

os.environ['MASTERLINK_NATIONAL_ID'] = 'A123456789'
os.environ['MASTERLINK_ACCOUNT'] = 'account'
os.environ['MASTERLINK_ACCOUNT_PASS'] = 'password'
os.environ['MASTERLINK_CERT_PATH'] = '/path/to/cert'
os.environ['MASTERLINK_CERT_PASS'] = 'cert_password'

acc = MasterlinkAccount()
```

---

### Fubon (富邦證券)

**Import:**
```python
from finlab.online.fubon_account import FubonAccount
```

**Environment Variables:**
```bash
export FUBON_NATIONAL_ID='A123456789'
export FUBON_ACCOUNT_PASS='password'
export FUBON_CERT_PATH='/path/to/cert.pfx'
```

**Usage:**
```python
import os

os.environ['FUBON_NATIONAL_ID'] = 'A123456789'
os.environ['FUBON_ACCOUNT_PASS'] = 'password'
os.environ['FUBON_CERT_PATH'] = '/path/to/cert.pfx'

acc = FubonAccount()
```

---

## OrderExecutor Class

The `OrderExecutor` manages order creation, modification, and cancellation.

**Import:**
```python
from finlab.online.order_executor import OrderExecutor
```

**Signature:**
```python
OrderExecutor(
    target_position: Position | dict,
    account: BrokerAccount
) -> OrderExecutor
```

**Parameters:**
- `target_position` (Position or dict, required): Target position to execute; a dict is converted with `Position(...)`
- `account` (BrokerAccount, required): Connected broker account instance

**Example:**
```python
from finlab.online.order_executor import OrderExecutor, Position
from finlab.online.sinopac_account import SinopacAccount

# Setup
position = Position.from_report(report, fund=1000000)
acc = SinopacAccount()
executor = OrderExecutor(position, account=acc)
```

---

### OrderExecutor Methods

#### show_alerting_stocks()

Display stocks that require pre-deposit (處置股/警示股).

```python
executor.show_alerting_stocks()
```

---

#### create_orders()

Create orders based on the target position.

**Signature:**
```python
create_orders(view_only: bool = False, ...) -> list[dict]
```

**Parameters:**
- `view_only` (bool, default=False): If True, preview orders without execution

**Returns:**
- `list[dict]`: The orders placed (or, with `view_only=True`, the orders that would be placed)

**Example:**
```python
# Preview orders first (recommended)
executor.create_orders(view_only=True)

# Execute orders
executor.create_orders()
```

---

#### update_order_price()

Update limit price for pending orders.

```python
executor.update_order_price()
```

---

#### cancel_orders()

Cancel all pending orders.

```python
executor.cancel_orders()
```

---

#### generate_orders() / generate_order_entries()

*(v1.5.9)* Compute the order diff (current position → target position) without sending anything to the broker. Useful for dry-runs, order inspection, and custom execution pipelines.

**Signature:**
```python
executor.generate_orders(
    progress: float = 1,
    progress_precision: int | None = 0,
    as_entries: bool | None = None,   # None → list[dict]
    quantity_type: str = 'decimal'    # 'decimal' | 'float' | 'string'
) -> list[dict] | list[OrderEntry]

# typed convenience API
executor.generate_order_entries(
    progress: float = 1,
    progress_precision: int = 0,
    quantity_type: str = 'decimal'
) -> list[OrderEntry]
```

`quantity` is in lots (see [Position Class](#position-class)): positive = buy, negative = sell. `quantity_type` sets the Python type of `OrderEntry.quantity`, not its unit, and is ignored when `generate_orders()` returns dicts.

**Example:**
```python
# Raw dict list (legacy)
orders = executor.generate_orders()

# Typed OrderEntry list — preferred for new code
entries = executor.generate_order_entries()
for e in entries:
    print(f"{e.symbol} qty={e.quantity}")
```

---

## Check Account Position

Query current holdings from broker.

```python
# Get current holdings
print(acc.get_position())
```

---

## PortfolioSyncManager — Typed Data APIs

*(v1.5.9)* In addition to `to_path()` / `from_path()` / `to_local()` / `from_local()` / `to_cloud()` / `from_cloud()`, `PortfolioSyncManager` now exposes typed data access:

```python
from finlab.portfolio import PortfolioSyncManager
from finlab.schemas import PortfolioData

pm = PortfolioSyncManager(...)

# Untyped dict — legacy
raw = pm.get_data()
pm.set_data(raw)

# Typed — preferred for new code
data: PortfolioData = pm.get_data_typed()
pm.set_data_typed(data)
```

The typed pair validates the payload against the `PortfolioData` schema at the boundary, so schema regressions surface immediately instead of propagating into persisted state.

---

## Realtime Position Streaming — `PositionStreamMixin`

*(v2.0.0)* `RealtimeProvider` subclasses auto-inherit a `subscribe_positions()` / `on_position()` interface for push-based position updates. Internally this uses a hybrid strategy — initialize via `get_position()`, update in real-time via broker Fill events, and periodically reconcile via polling (default 30s).

```python
from finlab.online.sinopac_account import SinopacAccount

acc = SinopacAccount()

def on_update(update):
    # update is a PositionUpdate: a snapshot of the whole account
    # (account_id, broker, position: Position, time, source='poll' | 'fill')
    for e in update.position:
        print(update.source, e['symbol'], e['quantity'], e['order_condition'])

# Register the callback first: subscribe_positions() emits the initial snapshot immediately
acc.on_position(on_update)
acc.subscribe_positions()
```

**Why hybrid:** Fill-event streams catch fills with sub-second latency but can miss events during disconnects; polling catches missed state but is slow. Combining both gives real-time responsiveness without state divergence risk.

The callback fires only when the snapshot changes (deduplicated internally via `PositionUpdate.snapshot_key()`).

---

## Cloud Strategy Deployment — `python -m finlab cloud` *(v2.0.1)*

For users who want a strategy to run automatically on a schedule (daily by default; market holidays are not skipped) without managing their own server, FinLab ships a CLI that deploys the strategy to the `finlab-auto-update` Cloud Functions runtime (Asia/Taipei schedule). This is operational tooling — it does not place broker orders by itself; pair it with the `OrderExecutor` workflow above if you want the cloud run to fire live trades.

### Command Map

```bash
python -m finlab cloud deploy <sid>     # upload strategy and (optionally) schedule it
python -m finlab cloud get    <sid>     # inspect metadata + inline source
python -m finlab cloud list             # list deployed strategies
python -m finlab cloud run    <sid>     # trigger one ad-hoc execution
python -m finlab cloud logs   <sid>     # recent execution history
python -m finlab cloud schedule set <sid> HH:MM   # e.g. schedule set my-strat 14:30
python -m finlab cloud schedule delete <sid>
python -m finlab cloud delete <sid>     # remove strategy + schedule (history preserved)
python -m finlab cloud status           # monthly budget / tier usage
```

`<sid>` is your strategy identifier: it must start with a letter or number, contain only letters, numbers, `.`, `_`, and `-`, and be at most 64 characters. Keep it stable — it is used as the Firestore document id.

### Deploy

**Single file:**
```bash
python -m finlab cloud deploy my_value_strategy \
  --code strategy.py \
  --time 14:35 \
  --tier s
```

**Multi-file project (zip):**
```bash
python -m finlab cloud deploy my_value_strategy \
  --zip project.zip --entry-script main.py \
  --time 14:35 --tier m
```

**Key flags:**
- `--code <file.py>` *or* `--zip <archive.zip> --entry-script <relpath.py>` — choose one. Zip is for multi-file strategies.
- `--time HH:MM` — daily trigger time in Asia/Taipei. Omit on a new SID to deploy without a schedule (run manually with `cloud run`); re-deploying an existing SID without `--time` keeps its current schedule — stop it with `cloud schedule delete <sid>`.
- `--tier {s,m,l,xl}` — compute tier. Larger tiers cost more per run; check `cloud status` for available tiers and monthly budget.
- `--contest` / `--no-contest` / `--contest-alias <name>` — participate in FinLab's strategy contest under an alias.

### Inspect, Trigger, Monitor

```bash
# Read back what's deployed
python -m finlab cloud get my_value_strategy --code-only > strategy_remote.py

# Trigger a one-off run (rate-limited: 5/hour per strategy)
python -m finlab cloud run my_value_strategy --tier m

# See the last few executions including stdout/stderr
python -m finlab cloud logs my_value_strategy --show-output
```

`cloud list` and `cloud logs` give you SID, tier, schedule, type, contest status, runtime, cost, and queue time per run.

### Budget Awareness

```bash
python -m finlab cloud status                # current month
python -m finlab cloud status --month 2026-04
```

Returns monthly budget, used quota, remaining quota, available tiers, and execution counts (success / error / timeout). Check this before deploying a high-tier strategy; you cannot exceed the monthly budget.

### Typical Flow

```bash
# 1. Local development — finalize strategy in strategy.py and verify with sim()
python -m finlab cloud deploy momentum_top10 --code strategy.py --time 13:35 --tier s

# 2. Confirm it ran today
python -m finlab cloud logs momentum_top10 --show-output

# 3. Iterate: redeploy overwrites the existing SID's code and schedule
python -m finlab cloud deploy momentum_top10 --code strategy.py --time 14:00 --tier m

# 4. Pause for the weekend
python -m finlab cloud schedule delete momentum_top10
```

---

## Related References

- [backtesting-reference.md](backtesting-reference.md): Backtest configuration and report generation
- [best-practices.md](best-practices.md): Coding patterns and anti-patterns
