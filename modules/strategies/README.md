# Strategy Input Contract — NON-NEGOTIABLE

All strategies in qaai_system MUST obey this rule:

> A strategy is a pure function of `StrategyContext`.

## Allowed
- Read fields from StrategyContext
- Compute signals
- Return decisions

## Forbidden
- Fetching data
- Calling providers
- Accessing stores
- Reading globals
- Mutating context

## Why This Exists
- Determinism
- Backtest/live parity
- Safe evolution
- Capital allocation correctness (Phase G)

Violation of this rule is a hard architecture error.
