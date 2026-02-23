# CI/CD Pipeline — qaai_system

## Pipeline Stages

1. Lint & Static Checks
2. Unit Tests (100% pass required)
3. Integration Tests
4. Backtest Determinism Check
5. Governance Guard Check
6. Build Artifact
7. Deploy (manual approval)

## Mandatory Gates
- Any failed test → STOP
- Any uncommitted approval file → STOP
- Any missing audit hook → STOP

## Deployment Rule
No direct production deploys.
All releases are tagged and signed.
