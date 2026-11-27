# Cloud Strategy Deployment Reference — `python -m finlab cloud` *(v2.0.1)*

For users who want a strategy to run automatically on a schedule (Asia/Taipei time, daily by default, market holidays not skipped) without managing their own server, FinLab ships a CLI that deploys the strategy to the `finlab-auto-update` Cloud Functions runtime. It runs the strategy on that schedule; it does not place orders.

## Command Map

```bash
python -m finlab cloud deploy <sid>     # upload strategy and (optionally) schedule it
python -m finlab cloud get    <sid>     # inspect metadata + inline source
python -m finlab cloud list             # list deployed strategies
python -m finlab cloud run    <sid>     # trigger one ad-hoc execution
python -m finlab cloud logs   <sid>     # recent execution history
python -m finlab cloud schedule set <sid> [HH:MM] # time optional for custom cron
python -m finlab cloud schedule delete <sid>      # remove schedule until set again
python -m finlab cloud delete <sid>     # remove strategy + schedule (history preserved)
python -m finlab cloud status           # monthly budget / tier usage
```

`<sid>` is your strategy identifier: up to 64 letters, numbers, `.`, `_`, or `-`, starting with a letter or number. Keep it stable — it is the Firestore document id.

## Deploy

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
- `--time HH:MM` — trigger time in Asia/Taipei (daily by default). Without `--time` or frequency options, a new SID gets no schedule (run manually with `cloud run`) and an existing SID keeps its current one.
- `--frequency {daily,weekly,monthly,custom}` *(v2.2.9)* — available on both `cloud deploy` and `cloud schedule set`. Use `--time HH:MM` on deploy or positional `HH:MM` on schedule set, except for custom cron.
- `--days-of-week 1,2,3,4,5` — required for `--frequency weekly`; 0=Sunday through 6=Saturday. Weekdays still include market holidays.
- `--day-of-month 1-31` — required for `--frequency monthly`; months without that date are skipped.
- `--cron "35 14 * * 1-5"` — required for `--frequency custom`; a numeric five-field cron (minute, hour, day, month, weekday) in Asia/Taipei, with no separate time required.
- `--tier {s,m,l,xl}` — compute tier. Larger tiers cost more per run; check `cloud status` for available tiers and monthly budget.
- `--contest` / `--no-contest` / `--contest-alias <name>` — participate in FinLab's strategy contest under an alias.

## Schedule Examples

```bash
# Weekdays at 14:35 (also works with deploy --code strategy.py --time 14:35)
python -m finlab cloud schedule set my_value_strategy 14:35 --frequency weekly --days-of-week 1,2,3,4,5

# The first of each month at 14:35
python -m finlab cloud schedule set my_value_strategy 14:35 --frequency monthly --day-of-month 1

# Custom cron: weekdays at 14:35, without a separate HH:MM argument
python -m finlab cloud schedule set my_value_strategy --frequency custom --cron "35 14 * * 1-5"
```

`cloud schedule delete <sid>` removes the schedule; it does not pause until Monday or resume automatically. Restore automatic runs with `cloud schedule set`.

## Inspect, Trigger, Monitor

```bash
# Read back what's deployed
python -m finlab cloud get my_value_strategy --code-only > strategy_remote.py

# Trigger a one-off run (rate-limited: 5/hour per strategy)
python -m finlab cloud run my_value_strategy --tier m

# See the last few executions including stdout/stderr
python -m finlab cloud logs my_value_strategy --show-output
```

`cloud list` and `cloud logs` give you SID, tier, schedule, type, contest status, runtime, cost, and queue time per run.

## Budget Awareness

```bash
python -m finlab cloud status                # current month
python -m finlab cloud status --month 2026-04
```

Returns monthly budget, used quota, remaining quota, available tiers, and execution counts (success / error / timeout). Check this before deploying a high-tier strategy; you cannot exceed the monthly budget.

## Typical Flow

```bash
# 1. Local development — finalize strategy in strategy.py and verify with sim()
python -m finlab cloud deploy momentum_top10 --code strategy.py --time 13:35 --tier s

# 2. Confirm it ran today
python -m finlab cloud logs momentum_top10 --show-output

# 3. Iterate: redeploy overwrites the existing SID's code and schedule
python -m finlab cloud deploy momentum_top10 --code strategy.py --time 14:00 --tier m

# 4. Run only on weekdays; the schedule continues automatically next Monday
python -m finlab cloud schedule set momentum_top10 14:00 --frequency weekly --days-of-week 1,2,3,4,5
```

---

## Related References

- [backtesting-reference.md](backtesting-reference.md): Backtest configuration and report generation
- [best-practices.md](best-practices.md): Coding patterns and anti-patterns
