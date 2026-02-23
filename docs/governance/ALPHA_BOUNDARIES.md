# Alpha Boundaries — Shadow Live Phase

## Core Principle
In Shadow Live, alpha intelligence may OBSERVE reality but must NEVER CHANGE it.

This document defines non-negotiable boundaries for alpha behavior prior to
Paper Trading.

Violation of any rule below is a governance defect.

---

## ❌ Alpha Components FORBIDDEN in Shadow Live

### 1. Execution Modification
Alpha MUST NOT:
- Change entry timing
- Change order type
- Change BUY/SELL side
- Cancel or replace execution intents

Reason:
Breaks determinism, replay, and auditability.

Allowed only from: Paper Trading

---

### 2. Position Sizing or Leverage
Alpha MUST NOT:
- Adjust quantity
- Apply confidence-based sizing
- Apply volatility sizing
- Use Kelly or adaptive leverage

Reason:
This is capital logic and must be validated with virtual capital first.

Allowed only from: Paper Trading

---

### 3. Capital Allocation
Alpha MUST NOT:
- Allocate capital across strategies
- Enable/disable strategies
- Rotate capital budgets

Reason:
Capital governance precedes intelligence.

Allowed only from: Meta-Alpha phase

---

### 4. Alpha Feedback Loops
Alpha MUST NOT:
- Learn from live outcomes
- Retrain online
- Adapt thresholds dynamically
- Modify itself based on recent performance

Reason:
Introduces hidden state and breaks reproducibility.

Allowed only from: Paper Trading (offline learning)

---

### 5. Auto-Promotion or Auto-Termination
Alpha MUST NOT:
- Promote strategies automatically
- Kill strategies automatically
- Gate execution based on alpha confidence

Reason:
Strategy lifecycle decisions require explicit governance.

Allowed only from: Strategy Lifecycle phase

---

### 6. Risk Overrides
Alpha MUST NOT:
- Override risk limits
- Ignore drawdown rules
- Bypass throttles

Reason:
Intelligence must never override hard risk controls.

Allowed: NEVER

---

## ✅ Alpha Components ALLOWED in Shadow Live

- Observational diagnostics
- Parallel shadow strategies
- Counterfactual analysis
- Explainability
- Regime detection
- Probability estimates

All allowed components:
- Are read-only
- Produce telemetry only
- Have zero execution authority
- Have zero capital authority

---

## Enforcement Rule
Any alpha component that requires execution or capital authority
cannot exist in Shadow Live.

Shadow Live is a learning phase, not an acting phase.
