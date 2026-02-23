# Environment Matrix — qaai_system

| Environment | Broker | Capital | Execution | Purpose |
|------------|--------|---------|-----------|---------|
| DEV | None | SIM | Disabled | Local development |
| BACKTEST | None | SIM | Backtest | Strategy research |
| PAPER | PaperBroker | SIM | Enabled | Validation |
| LIVE-SANDBOX | Broker Sandbox | REAL | Limited | Canary |
| LIVE | Broker Prod | REAL | Enabled | Production |

## Rules
- No environment shares state or credentials
- LIVE cannot run without approvals
- PAPER and LIVE data paths are isolated

## Absolute Rule
If environment is unclear → execution is blocked
