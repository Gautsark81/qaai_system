## Failure Scenarios

### Broker Down
- Detect via heartbeat loss
- Halt trading
- Alert operator
- Reconcile once broker recovers

### Data Feed Gap
- Halt trading immediately
- Do NOT extrapolate prices

### Duplicate Execution Risk
- Enforced by idempotency keys
- Replay-safe execution
