from datetime import datetime, timezone
from typing import List

from core.strategy_factory.registry import StrategyRegistry
from core.phase_b.confidence import ConfidenceEngine

from modules.operator_dashboard.contracts.dashboard_snapshot import (
    DashboardSnapshot,
)
from modules.operator_dashboard.contracts.oversight import (
    OversightEventSnapshot,
)
from modules.operator_dashboard.adapters.oversight_adapter import (
    get_oversight_event_snapshots,
)

from modules.operator_dashboard.snapshot import (
    get_system_health_snapshot,
    get_capital_snapshot,
    get_regime_snapshot,
    get_strategy_snapshots,
    get_alerts_snapshot,
    get_explainability_snapshot,
)

from core.live_verification.integration import LiveVerificationEngine


class DashboardStateAssembler:
    """
    Safe, stateless assembler for UI tests, previews, and CI snapshots.
    """

    # -----------------------------------------------------------------
    # CI SNAPSHOT ENTRYPOINT (ABSOLUTELY SCHEMA-LOCKED)
    # -----------------------------------------------------------------
    @classmethod
    def assemble(cls) -> DashboardSnapshot:

        registry = StrategyRegistry()
        confidence_engine = ConfidenceEngine(registry)

        strategy_map = get_strategy_snapshots(
            registry=registry,
            confidence_engine=confidence_engine,
        )

        return DashboardSnapshot(
            timestamp=datetime(2025, 12, 29, 13, 6, 46, 872020, tzinfo=timezone.utc),
            system=get_system_health_snapshot(),
            strategies=list(strategy_map.values()),
            alerts=list(get_alerts_snapshot()),
            capital=get_capital_snapshot(),
            regime=None,
            explainability=None,
            oversight_events=None,
        )

    # -----------------------------------------------------------------
    # FULL UI ASSEMBLY (RUNTIME ONLY — NOT CI)
    # -----------------------------------------------------------------
    def assemble_full(self) -> DashboardSnapshot:

        registry = StrategyRegistry.global_instance()
        confidence_engine = ConfidenceEngine(registry)

        oversight_events: List[OversightEventSnapshot] = (
            get_oversight_event_snapshots()
        )

        strategy_map = get_strategy_snapshots(
            registry=registry,
            confidence_engine=confidence_engine,
        )

        explainability = dict(get_explainability_snapshot() or {})
        alerts = list(get_alerts_snapshot())

        # -----------------------------------------------------------------
        # C19.3 — Institutional Live Proof Intelligence Layer
        # -----------------------------------------------------------------
        try:
            import time

            verifier = LiveVerificationEngine.global_instance()
            artifacts = verifier.list_artifacts()

            total = len(artifacts)
            current_ts = time.time()

            if total == 0:
                proof_gap = True

                explainability["live_proof"] = {
                    "total_artifacts": 0,
                    "last_hash": None,
                    "authority_all_valid": True,
                    "unique_hash_ratio": 1.0,
                    "chain_integrity_score": 1.0,
                    "proof_gap_detected": proof_gap,
                    "duplicate_hash_detected": False,
                }

            else:
                hashes = [a.chain_hash for a in artifacts]
                unique_hashes = set(hashes)

                authority_all_valid = all(
                    a.authority_validated for a in artifacts
                )

                duplicate_hash_detected = len(unique_hashes) != total
                unique_hash_ratio = len(unique_hashes) / total

                # -----------------------------
                # Inactivity Sentinel (60 sec SLA)
                # -----------------------------
                last_trace = artifacts[-1].trace
                last_timestamp = getattr(last_trace, "timestamp", None)

                if last_timestamp:
                    gap_seconds = current_ts - last_timestamp.timestamp()
                    proof_gap = gap_seconds > 60
                else:
                    proof_gap = False

                chain_integrity_score = (
                    1.0
                    if authority_all_valid and not duplicate_hash_detected
                    else 0.0
                )

                explainability["live_proof"] = {
                    "total_artifacts": total,
                    "last_hash": artifacts[-1].chain_hash,
                    "authority_all_valid": authority_all_valid,
                    "unique_hash_ratio": round(unique_hash_ratio, 4),
                    "chain_integrity_score": chain_integrity_score,
                    "proof_gap_detected": proof_gap,
                    "duplicate_hash_detected": duplicate_hash_detected,
                }

                # -----------------------------
                # Automatic Alert Injection
                # -----------------------------
                if chain_integrity_score < 1.0:
                    alerts.append(
                        {
                            "type": "LIVE_PROOF_INTEGRITY_FAILURE",
                            "severity": "CRITICAL",
                            "message": "Live proof chain integrity compromised.",
                        }
                    )

                if proof_gap:
                    alerts.append(
                        {
                            "type": "LIVE_PROOF_INACTIVITY",
                            "severity": "WARNING",
                            "message": "No live proof artifacts generated recently.",
                        }
                    )

        except Exception:
            explainability["live_proof"] = {
                "error": "Live proof unavailable",
            }

        # -----------------------------------------------------------------

        return DashboardSnapshot(
            timestamp=datetime.now(timezone.utc),
            system=get_system_health_snapshot(),
            capital=get_capital_snapshot(),
            regime=get_regime_snapshot(),
            strategies=list(strategy_map.values()),
            alerts=alerts,  # ✅ USE MODIFIED ALERTS
            explainability=explainability,
            oversight_events=tuple(oversight_events),
        )

    # -----------------------------------------------------------------
    # Governance helpers
    # -----------------------------------------------------------------
    def assemble_lifecycle(self, records):
        return [
            type("LifecycleDTO", (), dict(record))()
            for record in records
        ]

    def assemble_approvals(self, records):
        return [
            type("ApprovalDTO", (), dict(record))()
            for record in records
        ]