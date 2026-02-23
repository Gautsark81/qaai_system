# MASTER BLUEPRINT — From Paper Trading → Live Dhan Deployment (FINAL)

Source: status_report.md and repository structure (structure.txt).
Status snapshot: coverage 74.0%, Final Score 62.2% (see status_report.md) :contentReference[oaicite:0]{index=0}.
Repo files & layout referenced from structure.txt. :contentReference[oaicite:1]{index=1}

---

## Executive summary (where you stand)

Health snapshot (key numbers):
- Coverage: 74.0% reported in status_report.md. :contentReference[oaicite:2]{index=2}
- Final Score: 62.2% (progress+stubs+core points combined). :contentReference[oaicite:3]{index=3}
- TODOs/FIXMEs/Stubs flagged: heavy (see status_report.md). :contentReference[oaicite:4]{index=4}

What's solid:
- Backtester, CLI driver, basic strategies and logging exist.
- Core modules: backtester, portfolio backtest mode, risk metrics, execution scaffolds present. (see structure listing). :contentReference[oaicite:5]{index=5}

Critical gaps:
- Dhan live adapter finalization & sandbox tests.
- Enforceable risk manager wiring & kill switch.
- Durable order persistence & reconciliation.
- ML pipeline skeleton + feature snapshot persistence.
- CI/CD + secrets hardening.

---

## Goals (one-liners)
1. Stabilize execution + enforce safety gates (risk manager).  
2. Full observability + audit trails for every trade decision.  
3. Integrate Dhan live adapter; validate end-to-end in sandbox.  
4. Candidate promotion pipeline: offline → sandbox → canary → live.  
5. Build feedback loop & feature store for meta-learning.

---

## Phased Roadmap (ordered — execute sequentially)

### Phase 0 — Prepare (pre-work)
- Update `.env.example`, credential docs.
- Ensure `pytest` runs locally; resolve failing tests and coverage hotspots.
- Files: `status_report.md` used to triage failing/low coverage files. :contentReference[oaicite:6]{index=6}

### Phase 1 — Stabilize Execution & Safety (MUST before live)
Goal: deterministic, auditable routing, and enforceable risk checks.

High-priority tasks:
- Implement and wire `execution/risk_manager.py` checks:
  - `check_kill_switch()`, `check_daily_loss()`, `check_symbol_cap()`, `reserve_notional()`.
  - Wire checks into `execution/orchestrator.py` pre-route hook.
- Finish `infra/dhan_adapter.py` sandbox mode: idempotent `client_order_id`, retries, sandbox auth.
- Durable order store: `db/orders.py` (upsert & reconciliation).
- Simulator: SL/TP & partial-fill behavior — `backtester/backtester.py`, `execution/bracket_manager.py`.

Acceptance criteria:
- Unit tests show risk checks block disallowed orders.
- Sandbox Dhan adapter integration tests pass.
- Order store persists & reconciles fills across restarts.

### Phase 2 — Observability, Reconciliation & Ops
Goal: real-time debuggability and auditability.

Tasks:
- Metrics: Prometheus metrics and Streamlit/Grafana dashboards; files: `monitoring/metrics.py`, `dashboard/streamlit_app.py`.
- Structured JSON logs including `trace_id`, `net_plan_id`, `signal_snapshot`, `risk_decision`.
- Reconcile job `infra/reconcile.py`.
- Debug endpoints: `/debug/net_plans/{id}`, `/debug/positions/{symbol}`.

Acceptance:
- Dashboards show test runs (backtest & sandbox).
- Reconciliation job detects injected mismatches in test.

### Phase 3 — Candidate Promotion & Safe Canarying
Goal: safe promotion path for strategy/model updates.

Tasks:
- Learning skeleton: `learning/trainer.py`, `learning/evaluator.py`, `learning/updater.py`.
- Model registry: `infra/model_registry.py`.
- Safe promote flow: offline validation → sandbox → canary (tiny notional) → live with auto-monitor & rollback.

Acceptance:
- Candidate can be registered, validated offline, sandboxed, promoted to canary, and automatically rolled back.

### Phase 4 — Meta-Learning & Autonomy
Goal: feature store + meta-controller.

Tasks:
- Feature store: `features/feature_store.py` — persist per-trade snapshots & labels.
- Meta-controller: `learning/meta_controller.py` — LinUCB / Thompson or LightGBM to update strategy weights.
- Candidate generator: `learning/candidate_generator.py` (GA/SMBO).

Acceptance:
- Meta-controller demonstrably improves sandbox metrics during experiments.

### Phase 5 — Scale & Harden
Goal: infra, secrets, HA, multi-asset.

Tasks:
- CI/CD: GitHub Actions (tests, lint, build), container images.
- Secrets: Vault/AWS Secrets Manager integration.
- HA infra: Docker Compose/K8s templates, healthchecks.
- Multi-asset: add options/futures adapters + margin models.

Acceptance:
- System runs reproducibly in container; secrets removed from repo; rollbacks tested.

---

## File → Task mapping (copy/paste issues)
(High-priority selection)
- `execution/risk_manager.py` + `execution/orchestrator.py` — implement pre-route checks; tests `tests/test_risk_manager.py`.
- `infra/dhan_adapter.py`, `infra/dhan_client.py`, `tests/test_dhan_adapter_sandbox.py` — finalize sandbox adapter.
- `db/orders.py`, `backtester/backtester.py` — durable order store & JSONL additions (persist `simulation_config` & `feature_snapshot`).
- `execution/bracket_manager.py`, `backtester/backtester.py`, `tests/test_partial_fills.py` — partial fills & bracket orders.
- `learning/meta_controller.py`, `learning/updater.py`, `infra/model_registry.py` — learning pipeline skeleton + safe_promote hooks.

---

## Observability & metrics (minimum)
Prometheus names:
- `orders_submitted_total`, `orders_filled_total`, `partial_fill_rate`, `avg_slippage_ms`, `daily_loss`, `kill_switch_trips_total`, `reconcile_mismatch_total`.

Logs:
- JSON events with `trace_id`, `net_plan_id`, `event_type`, `payload`.

Debug endpoints:
- `/debug/net_plans/{id}`, `/debug/positions/{symbol}`.

---

## Testing & Validation Matrix (automation required)
- Unit tests (CI): cover execution/risk_manager, orchestrator, position_store, backtester.
- Integration tests: Dhan sandbox end-to-end (submit/cancel/partial-fills).
- Backtest regression: seeded runs for reproducibility.
- Stress tests: provider downtime, slippage bursts.
- Canary safety tests: gating monitors for N trades/days.

---

## Current Status (Completed / In-progress / Pending)
**Completed**
- Backtester core (slippage/latency/JSONL logging) and many strategies & tests. (See `backtester/*` coverage). :contentReference[oaicite:7]{index=7}

**In Progress**
- `infra/dhan_adapter.py` exists but needs final sandbox wiring & idempotency tests (coverage indicates presence but not complete). :contentReference[oaicite:8]{index=8}
- `execution/risk_manager.py` present at 72% coverage — internal logic partly implemented; needs checks and orchestrator wiring. :contentReference[oaicite:9]{index=9}

**Pending / High Priority**
- Durable order & fill DB-backed store and reconciliation job (db persistence & `infra/reconcile.py`).
- Formal promotion pipeline (`learning/*` skeletons exist but need integration & audit hooks).
- Secrets & CI/CD improvements.
- Full bracket order / partial-fill simulation coverage.

(See full per-file coverage table in status_report.md for exact low-coverage files) :contentReference[oaicite:10]{index=10}

---

## Recommended next 6-step path (Phase 1 → 3 focus)
1. **Immediate (blockers)**: Implement & wire `execution/risk_manager.py` functions and add `tests/test_risk_manager.py`. (MUST)
2. **Sandbox infra**: Finalize `infra/dhan_adapter.py` sandbox integration and write integration tests. (MUST)
3. **Persistence**: Implement `db/orders.py` (upsert & reconciliation) and patch `backtester._persist_trade_log()` to include `simulation_config` & `feature_snapshot`.
4. **Simulator**: Add partial fills & bracket order simulation (`backtester/backtester.py` + `execution/bracket_manager.py`) and tests.
5. **Observability**: Instrument Prometheus metrics and simple Streamlit dashboard for debugging.
6. **Promotion flow**: Add `learning/updater.safe_promote()` + `infra/model_registry.py` and test offline → sandbox → canary.

---

## Acceptance criteria before live Dhan trading
- Phase 1 complete: risk manager, Dhan sandbox tests, durable persistence, SL/TP + partial fills.
- Observability (Phase 2) deployed and validated.
- Promotion path implemented and audited.
- Secrets removed from repo, CI passes, release pipeline exists.
- Runbook & human-in-the-loop approvals defined.

---

## Where I can help next
I can produce ready-to-drop code for one area now (examples):
- `execution/risk_manager.py` + unit tests. (High impact)
- `infra/dhan_adapter.py` sandbox harness + idempotency utilities.
- Patch `backtester._persist_trade_log()` to include `simulation_config` + `feature_snapshot`.
- `learning/updater.safe_promote()` with MLFlow stubs.
- `execution/aggregator.py` (signal aggregator & weighted netting) + tests.

Pick one and I’ll produce the full code + tests ready to paste.

