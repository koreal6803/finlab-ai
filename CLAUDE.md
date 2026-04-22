# FinLab Skill Project Optimizer

## Directive

You are maintaining documentation for a quantitative trading framework. **Mediocrity is unacceptable.** Every line must serve a purpose. Every example must compile and run. Every explanation must be technically precise.

Do not tolerate:
- Vague descriptions that could mean anything
- Broken code examples
- Redundant information that wastes reader time
- Hand-wavy explanations that avoid technical detail
- "Should work" or "might be useful" language

## Project Structure

```
finlab-plugin/skills/finlab/
├── SKILL.md                    # Main entry point - overview, quick start, core workflow
├── dataframe-reference.md      # FinLabDataFrame methods (is_largest, sustain, hold_until)
├── backtesting-reference.md    # sim() API, Report class, metrics extraction
├── trading-reference.md        # OrderExecutor, Position, broker account setup
├── factor-examples.md          # 60+ complete strategy examples (TW + short US syntax section)
├── factor-analysis-reference.md # IC, Shapley values, calc_metric, calc_centrality
├── best-practices.md           # Patterns, anti-patterns, error handling
├── machine-learning-reference.md # feature.combine, label generation, ML workflow
├── us-market.md                # US market: data map, quarterly alignment, defaults, universe construction
└── README.md                   # TODO/improvements tracker
```

## Documentation Quality Standards

### 1. Code Examples

Every code example MUST:
- **Compile without modification** - no pseudo-code, no placeholders
- **Import all dependencies** - never assume imports are obvious
- **Use realistic values** - not `x = 1` but `stop_loss = 0.08`
- **Show complete patterns** - from data fetch to result

```python
# BAD - incomplete, unclear
pos = cond1 & cond2
sim(pos)

# GOOD - complete, production-ready
from finlab import data
from finlab.backtest import sim

close = data.get("price:收盤價")
pb = data.get("price_earning_ratio:股價淨值比")

cond1 = close > close.average(60)
cond2 = pb.rank(axis=1, pct=True) < 0.3

position = pb[cond1 & cond2].is_smallest(10)
report = sim(position, resample="M", stop_loss=0.08, upload=False)
print(f"CAGR: {report.get_stats()['cagr']:.2%}")
```

### 2. Function Documentation

Every function MUST have:
- **Signature** - exact Python signature with type hints
- **Parameters** - type, required/optional, default value, what it does
- **Returns** - what type and what it contains
- **Example** - working code showing typical usage

```markdown
### function_name

Brief description of what it does - ONE sentence.

**Signature:**
python
function_name(
    required_param: Type,
    optional_param: Type = default
) -> ReturnType


**Parameters:**
- `required_param` (Type, required): What it does
- `optional_param` (Type, default=X): What it does

**Returns:**
- `ReturnType`: What the return value contains

**Example:**
python
# Working example code here
```

### 3. No Redundancy

- **Do not repeat information** across files
- **Cross-reference** using relative links: `See [backtesting-reference.md](backtesting-reference.md)`
- **Single source of truth** - each concept explained in ONE place

### 4. Hierarchy of Information

1. **Most common use case first** - 80% of readers need this
2. **Advanced options second** - for power users
3. **Edge cases last** - rare scenarios

## Optimization Checklist

When reviewing any skill file, verify:

### Technical Accuracy
- [ ] All code examples execute without error
- [ ] Function signatures match actual API
- [ ] Default values are documented correctly
- [ ] Return types are accurate

### Completeness
- [ ] Every public function is documented
- [ ] Common use cases have examples
- [ ] Error scenarios are explained
- [ ] Prerequisites are listed

### Conciseness
- [ ] No verbose explanations where code speaks clearer
- [ ] No duplicate information within same file
- [ ] No duplicate information across files (use links)
- [ ] Tables used for structured data, not prose

### Usability
- [ ] Quick copy-paste examples work
- [ ] Parameters are in logical order
- [ ] Related functions are grouped together
- [ ] Navigation (TOC, links) helps readers find info fast

## File-Specific Guidelines

### SKILL.md (Main Entry)
- Must contain working quick start example (< 20 lines)
- Must list all reference files with 1-line descriptions
- Must include prerequisites (API token, installation)
- Do NOT duplicate detailed reference content here

### dataframe-reference.md
- Every method: signature, params, returns, example
- Emphasize methods NOT in standard pandas
- Show method chaining patterns

### backtesting-reference.md
- Full `sim()` signature with all parameters
- `Report` class methods documented separately
- Key mappings table: `metrics.X()` vs `get_stats()['Y']`

### trading-reference.md
- Environment variable tables per broker
- Exact import paths
- Order execution workflow steps

### factor-examples.md
- Each example: title, brief description, complete code
- Group by category (technical, fundamental, chip, etc.)
- Code must run as-is

### factor-analysis-reference.md
- Focus on function signatures and workflows
- IC interpretation guidelines
- Shapley value computational complexity warning

### best-practices.md
- DO/DON'T format with concrete examples
- Anti-patterns with explanation of WHY it's wrong
- Error messages and solutions

### machine-learning-reference.md
- Complete workflow from feature to backtest
- Warn about look-ahead bias risks
- `feature.combine` vs `data.indicator` guidance

## Maintenance Philosophy

### Every Change Must

1. **Solve a real problem** - not hypothetical improvements
2. **Be testable** - verify code examples still work
3. **Maintain consistency** - follow established patterns in other files

### Version Control

- Commit messages: `<file>: <what changed>` (e.g., `backtesting-reference.md: Add trail_stop parameter docs`)
- One logical change per commit
- Keep README.md TODO list updated

### Quality Gates

Before any documentation change is complete:

1. **Code verification** - paste examples into Python, they run
2. **Cross-reference check** - links work, no orphan references
3. **Terminology consistency** - same terms used throughout
4. **Format validation** - markdown renders correctly

## Common Issues and Fixes

### Issue: Outdated API

```markdown
# Symptom: Example throws AttributeError

# Fix: Check actual finlab source, update signature
# Verify: Run updated example in Python
```

### Issue: Duplicate Information

```markdown
# Symptom: Same explanation in multiple files

# Fix: Keep in most relevant file, add link from others
# Example: data.universe() fully in best-practices.md,
#          link from backtesting-reference.md
```

### Issue: Incomplete Example

```markdown
# Symptom: Missing imports, undefined variables

# Fix: Add all necessary imports and setup code
# Rule: Reader should be able to copy-paste and run
```

### Issue: Vague Description

```markdown
# BAD
"Use this method to improve your strategy."

# GOOD
"Returns boolean DataFrame where True marks top N values per row.
Use for limiting position to fixed number of stocks."
```

## Command Reference

When user asks to optimize documentation:

```
1. Read target file completely
2. Run through optimization checklist
3. Identify specific issues (list them)
4. Fix issues one at a time
5. Verify fixes don't break cross-references
6. Update README.md TODO if needed
```

## Quality Metrics

A well-maintained skill should have:

- **Zero broken code examples** (test periodically)
- **Zero duplicate explanations** across files
- **100% coverage** of public API functions
- **Clear navigation** - reader finds answer in < 30 seconds
- **Minimal words** - remove anything that doesn't add information

---

Remember: This documentation is what stands between a user and building profitable trading strategies. Unclear documentation is broken documentation. Fix it.
