# Cloud Strategy Deployment Reference — `python -m finlab cloud` *(v2.0.1)*

Deploys a strategy to FinLab's `finlab-auto-update` Cloud Functions runtime and runs it on a schedule, with no server of your own. Schedules use Asia/Taipei time and do not skip market holidays. It does not place orders.

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

`<sid>` is your strategy identifier: up to 64 letters, numbers, `.`, `_`, or `-`, starting with a letter or number. Reuse the same SID to update a deployment: redeploying replaces its code.

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
- `--time HH:MM` — trigger time, daily unless `--frequency` says otherwise; pick a time after the strategy's data is final ([SKILL.md](SKILL.md#when-todays-taiwan-data-is-final)). Without `--time` or frequency options, a new SID gets no schedule (run manually with `cloud run`) and an existing SID keeps its current one.
- `--frequency {daily,weekly,monthly,custom}` *(v2.2.9)* — available on both `cloud deploy` and `cloud schedule set`. Use `--time HH:MM` on deploy or positional `HH:MM` on schedule set.
- `--days-of-week 1,2,3,4,5` — required for `--frequency weekly`; 0=Sunday through 6=Saturday.
- `--day-of-month 1-31` — required for `--frequency monthly`; months without that date are skipped.
- `--cron "35 14 * * 1-5"` — required for `--frequency custom`; a numeric five-field cron (minute, hour, day, month, weekday); no separate time needed.
- `--tier {s,m,l,xl}` — compute tier; larger tiers cost more per run.
- `--contest` / `--no-contest` / `--contest-alias <name>` — participate in FinLab's strategy contest under an alias.

## Schedule Examples

```bash
# Weekdays at 14:35 (also works with deploy --code strategy.py --time 14:35)
python -m finlab cloud schedule set my_value_strategy 14:35 --frequency weekly --days-of-week 1,2,3,4,5

# The first of each month at 14:35
python -m finlab cloud schedule set my_value_strategy 14:35 --frequency monthly --day-of-month 1

# Custom cron: weekdays at 14:35
python -m finlab cloud schedule set my_value_strategy --frequency custom --cron "35 14 * * 1-5"
```

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

---

## Related References

- [backtesting-reference.md](backtesting-reference.md#upload): cloud runs upload the `sim()` report automatically (`FINLAB_FORCED_STRATEGY_NAME`)
