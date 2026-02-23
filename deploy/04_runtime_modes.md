# Runtime Modes

## Modes
- INIT
- DATA_READY
- STRATEGY_READY
- PAPER
- LIVE

## Transitions
INIT → DATA_READY → STRATEGY_READY → PAPER → LIVE

## Forbidden
- Skipping states
- Auto transitions
- Runtime downgrade from LIVE without kill switch

## Enforcement
SystemState guards every executor
