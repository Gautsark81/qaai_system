# qaai_system — Production Readiness Checklist

## CODE
- [x] All tests passing
- [x] Chaos tests executed
- [x] Deterministic seeds
- [x] No secrets committed

## RISK
- [x] Kill-switch wired globally
- [x] Circuit breakers enabled
- [x] Drawdown caps verified
- [x] Broker-agnostic RiskManager

## EXECUTION
- [x] Idempotent order IDs
- [x] Failover broker tested
- [x] Retry limits enforced

## STRATEGY GOVERNANCE
- [x] Health + decay enforced
- [x] Selector blocks non-ACTIVE
- [x] Promotion gates locked

## OBSERVABILITY
- [x] Telemetry enabled
- [x] Audit export functional
- [x] Daily reports generated

## GO-LIVE STEPS
- [ ] 30-day paper run
- [ ] Kill-switch drill
- [ ] Broker outage drill
- [ ] Capital ramp at 10%

SIGN-OFF:
CTO _______   RISK _______   DATE _______
