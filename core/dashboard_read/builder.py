from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Callable, Dict
from datetime import timedelta
from core.dashboard_read.snapshot import SnapshotMeta, SystemSnapshot
from core.dashboard_read import fallbacks
from core.dashboard_read.errors import SnapshotBuildError
from core.dashboard_read.fingerprint import compute_snapshot_fingerprint
from dataclasses import replace


class SystemSnapshotBuilder:
    """
    D-3 / D-4 Snapshot Builder

    Guarantees:
    - Snapshot NEVER crashes due to wiring/import failures
    - system_health is atomic only on real provider failure
    - Diagnostic state is embedded immutably in SnapshotMeta
    """

    def __init__(
        self,
        execution_mode: str,
        market_status: str,
        system_version: str,
    ):
        self.execution_mode = execution_mode
        self.market_status = market_status
        self.system_version = system_version
        self._last_created_at: datetime | None = None
        self._failures: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # ATOMIC PROVIDER
    # ------------------------------------------------------------------

    def _atomic_build(
        self,
        name: str,
        builder: Callable,
        fallback: Callable,
    ):
        try:
            return builder()

        # Wiring / environment failures → degrade
        except (ImportError, AttributeError) as e:
            self._failures[name] = f"{type(e).__name__}: {e}"
            return fallback()

        # Real provider failure → atomic stop
        except Exception as e:
            raise SnapshotBuildError(
                f"Atomic provider failure [{name}]: {type(e).__name__}: {e}"
            ) from e

    # ------------------------------------------------------------------
    # SAFE PROVIDER
    # ------------------------------------------------------------------

    def _safe_build(
        self,
        name: str,
        builder: Callable,
        fallback: Callable,
    ):
        try:
            return builder()
        except Exception as e:
            self._failures[name] = f"{type(e).__name__}: {e}"
            return fallback()

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def build(self) -> SystemSnapshot:
        try:
            from core.dashboard_read.providers import (
                execution,
                system_health,
                market_state,
                pipeline,
                strategies,
                risk,
                capital,
                shadow,
                paper,
                incidents,
                compliance,
                ops,
            )

            execution_state = self._safe_build(
                "execution_state",
                execution.build_execution_state,
                fallbacks.fallback_execution_state,
            )

            system_health_state = self._atomic_build(
                "system_health",
                system_health.build_system_health,
                fallbacks.fallback_system_health,
            )

            market_state_state = self._safe_build(
                "market_state",
                market_state.build_market_state,
                fallbacks.fallback_market_state,
            )

            pipeline_state = self._safe_build(
                "pipeline_state",
                pipeline.build_pipeline_state,
                fallbacks.fallback_pipeline_state,
            )

            strategy_state = self._safe_build(
                "strategy_state",
                strategies.build_strategy_state,
                fallbacks.fallback_strategy_state,
            )

            risk_state = self._safe_build(
                "risk_state",
                risk.build_risk_state,
                fallbacks.fallback_risk_state,
            )

            capital_state = self._safe_build(
                "capital_state",
                capital.build_capital_state,
                fallbacks.fallback_capital_state,
            )

            shadow_state = self._safe_build(
                "shadow_state",
                shadow.build_shadow_state,
                fallbacks.fallback_shadow_state,
            )

            paper_state = self._safe_build(
                "paper_state",
                paper.build_paper_state,
                fallbacks.fallback_paper_state,
            )

            incidents_state = self._safe_build(
                "incidents",
                incidents.build_incident_state,
                fallbacks.fallback_incident_state,
            )

            compliance_state = self._safe_build(
                "compliance",
                compliance.build_compliance_state,
                fallbacks.fallback_compliance_state,
            )

            ops_state = self._safe_build(
                "ops_state",
                ops.build_ops_state,
                fallbacks.fallback_ops_state,
            )

            now = datetime.now(tz=timezone.utc)

            # Enforce monotonic snapshot timestamps (D-4.6)
            if self._last_created_at is not None and now <= self._last_created_at:
                now = self._last_created_at + timedelta(microseconds=1)

            self._last_created_at = now

            failures_copy = dict(self._failures)

            meta = SnapshotMeta(
                snapshot_id=f"SNAPSHOT_{uuid.uuid4().hex}",
                created_at=now,
                execution_mode=self.execution_mode,
                market_status=self.market_status,
                system_version=self.system_version,
                failures=failures_copy,
                failure_count=len(failures_copy),
                is_degraded=bool(failures_copy),
            )

            snapshot = SystemSnapshot(
                meta=meta,
                system_health=system_health_state,
                market_state=market_state_state,
                pipeline_state=pipeline_state,
                strategy_state=strategy_state,
                execution_state=execution_state,
                risk_state=risk_state,
                capital_state=capital_state,
                shadow_state=shadow_state,
                paper_state=paper_state,
                incidents=incidents_state,
                compliance=compliance_state,
                ops_state=ops_state,
            )

            fingerprint = compute_snapshot_fingerprint(snapshot)

            meta_with_fp = replace(snapshot.meta, fingerprint=fingerprint)

            return replace(snapshot, meta=meta_with_fp)

        except SnapshotBuildError:
            raise

        except Exception as e:
            raise SnapshotBuildError(
                f"Snapshot atomicity violated: {type(e).__name__}: {e}"
            ) from e

    # ------------------------------------------------------------------
    # DIAGNOSTICS
    # ------------------------------------------------------------------

    @property
    def failures(self) -> Dict[str, str]:
        return dict(self._failures)
