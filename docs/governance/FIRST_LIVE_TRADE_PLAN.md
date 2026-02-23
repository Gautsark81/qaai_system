# FIRST LIVE TRADE PLAN (Paper Approval Only)

Version: v1.0  
Status: DRAFT  
Prepared By: __________________  
Date: __________________  

---

## 1. Purpose & Scope

This document defines the plan, constraints, and approval conditions
for qaai_system’s **first ever live trade**.

⚠️ This plan does NOT authorize execution.
It is for **paper approval, dry runs, and governance review only**.

---

## 2. Trade Classification

- Trade Type:
  - [ ] Intraday
  - [ ] Delivery
  - [ ] Options
  - [ ] Futures

- Market:
  - [ ] NSE Equity
  - [ ] NSE Derivatives

- Strategy Category:
  - [ ] Single-strategy
  - [ ] Meta-model allocated
  - [ ] Manual strategy override (paper only)

---

## 3. Strategy Identity

- Strategy ID:
- Strategy Name:
- Strategy Version / Hash:
- Strategy DNA Summary:
  - Entry Logic:
  - Exit Logic:
  - Stop Logic:
  - Time Constraints:

- Backtest Coverage:
  - Period:
  - Market Regimes Seen:
  - Max Drawdown:
  - Win Rate:
  - Strategy Success Ratio (SSR):

---

## 4. Symbol & Market Context

- Symbol:
- Sector:
- Liquidity Tier:
- Average Daily Volume:
- Volatility Regime (current):

- Reason for Selecting This Symbol:
  - [ ] High liquidity
  - [ ] Stable behavior
  - [ ] Clean spread
  - [ ] Representative test case

---

## 5. Capital & Risk Envelope

- Total Account Capital:
- Capital Allocated to This Trade:
- % of Account:
- Max Loss Allowed (₹):
- Max Loss Allowed (%):

Risk Controls Enabled:
- [x] Position size sanity check
- [x] ATR-based stop
- [x] Volatility regime filter
- [x] Symbol concentration cap
- [x] Kill switch (manual)

Expected Worst-Case Outcome:
- Loss (₹):
- Slippage assumptions:

---

## 6. Execution Constraints

- Order Type:
  - [ ] Market
  - [ ] Limit
- Max Slippage Allowed:
- Max Retry Count:
- Idempotency Enabled: YES / NO
- Broker Adapter: __________________

Execution Preconditions:
- RiskManager PASS required
- BuyingPowerModel PASS required
- ExecutionJournal writable
- Reconciliation loop active

---

## 7. Observability & Monitoring

Live Monitoring Interfaces:
- [ ] Execution Journal
- [ ] Order Manager logs
- [ ] Risk decision logs
- [ ] Capital snapshot
- [ ] Operator dashboard

Alerting:
- [ ] Order rejected
- [ ] Partial fill
- [ ] Unexpected retry
- [ ] Kill switch engaged

---

## 8. Operator Roles & Responsibilities

Primary Operator:
Backup Operator:
Escalation Contact:

Operator Authority:
- [ ] Can halt system
- [ ] Can cancel order
- [ ] Can disable strategy
- [ ] Can disconnect broker

---

## 9. Failure Scenarios & Responses

| Scenario | Expected System Response | Operator Action |
|--------|-------------------------|----------------|
| Order rejected | Retry / abort | Review logs |
| Partial fill | Reconcile | Decide exit |
| Risk breach | Hard block | No override |
| System crash | Safe halt | Manual check |
| Broker outage | Freeze | No re-entry |

---

## 10. Success Criteria (Paper)

This trade plan is considered **approved (paper)** if:

- [ ] All risk checks pass deterministically
- [ ] No rule overrides required
- [ ] Execution path is fully explainable
- [ ] Operator actions are clear
- [ ] Post-trade reconciliation is defined

---

## 11. Explicit Non-Goals

This plan does NOT allow:
- Scaling
- Strategy rotation
- Capital increase
- Auto-promotion
- Override of risk rules

---

## 12. Approval Sign-Off (Paper Only)

Prepared By: __________________  Date: __________  
Reviewed By: __________________  Date: __________  
Approved For Paper Only: YES / NO

