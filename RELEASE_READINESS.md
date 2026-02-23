# RELEASE READINESS CHECKLIST

This file lists gates that must pass before enabling any live/real-money trading.

## Safety & tests
- [ ] All unit tests pass (`pytest -q`).
- [ ] Integration dry-run smoke tests pass (`pytest tests/integration -q`).
- [ ] Critical modules coverage >= 80%:
  - execution/router.py
  - execution/orchestrator.py
  - infra/dhan_client.py (or equivalent)
  - db/db_utils.py
  - execution/risk_manager.py
  - main_orchestrator.py

## Code debt
- [ ] All `blocking` TODOs are assigned to issues and have owners.
- [ ] No unaddressed FIXMEs in execution / risk / infra / db.

## Simulation & Fail-safes
- [ ] Dry-run tests simulate partial fills, disconnects, delays.
- [ ] Global kill-switch is present and tested.
- [ ] Emergency unwind behavior tested.

## Observability & monitoring
- [ ] Structured logging in place with request/trace ids.
- [ ] Metrics and alerting rules for critical failures present.

## Governance & process
- [ ] CI enforces blocking TODOs and coverage gates.
- [ ] Release plan with canary and rollback documented.
- [ ] Human in the loop approvals for first live deployments.

## Deployment
- [ ] Run final dry-run on the target environment (staging) and validate replay & reconciliation.
