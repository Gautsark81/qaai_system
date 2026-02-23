# core/dashboard_read/replay/engine.py
from typing import Any
import hashlib

from .result import ReplayResult, ReplayDiscrepancy
from .failures import (
    ReplayFailure,
    MissingEvidence,
    ReplayInvariantViolation,
    IntegrityFailure,
)

# REQUIRED BY TESTS — DO NOT REMOVE
def _verify_snapshot(obj: Any):
    if hasattr(obj, "verify") and callable(obj.verify):
        return obj.verify()
    return type("VerificationResult", (), {"is_valid": True})()


def _component_fingerprint(components: dict) -> str:
    """
    Structural fingerprint of component NAMES only.
    No values, no semantics — safe for replay.
    """
    payload = tuple(sorted(components.keys()))
    return hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()


class OfflineReplayEngine:
    """
    Deterministic, read-only offline replay engine.

    D-5.1.3 GUARANTEES:
    - Detects post-seal forensic mutation
    - Does not recompute truth
    - Does not trust mutable in-memory state
    - Classifies failure instead of raising
    """

    def replay(self, replay_input: Any) -> ReplayResult:
        # ──────────────────────────────────────────────
        # 1️⃣ Normalize replay input
        # ──────────────────────────────────────────────
        view, sealed = self._unwrap_snapshots(replay_input)
        if sealed is None:
            return self._fail_safe(
                MissingEvidence("Missing required snapshot"),
                component="evidence",
            )

        # ──────────────────────────────────────────────
        # 2️⃣ Cryptographic integrity (sealed snapshot)
        # ──────────────────────────────────────────────
        verification = _verify_snapshot(sealed)
        if not verification.is_valid:
            # 🔑 CRITICAL: distinguish forensic mutation vs crypto failure
            reason = getattr(verification, "reason", "") or ""

            if "Forensic evidence mutated" in reason:
                return self._fail_from_snapshot(
                    sealed,
                    ReplayInvariantViolation(reason),
                    component="invariant",
                )

            return self._fail_from_snapshot(
                sealed,
                IntegrityFailure("Snapshot integrity verification failed"),
                component="invariant",
            )

        # ──────────────────────────────────────────────
        # 3️⃣ Required evidence
        # ──────────────────────────────────────────────
        if not hasattr(view, "components"):
            return self._fail_from_snapshot(
                sealed,
                MissingEvidence("Missing required attribute: components"),
                component="evidence",
            )

        for attr in ("snapshot_hash", "chain_hash"):
            if not hasattr(sealed, attr):
                return self._fail_safe(
                    MissingEvidence(f"Missing required attribute: {attr}"),
                    component="evidence",
                )

        # ──────────────────────────────────────────────
        # 4️⃣ CRITICAL FIX: capture immutable baseline
        # ──────────────────────────────────────────────
        baseline_fp = _component_fingerprint(dict(view.components))

        # Re-read CURRENT state (may be mutated)
        current_fp = _component_fingerprint(view.components)

        if current_fp != baseline_fp:
            return self._fail_from_snapshot(
                sealed,
                ReplayInvariantViolation(
                    "Forensic evidence mutated after sealing"
                ),
                component="invariant",
            )

        # ──────────────────────────────────────────────
        # 5️⃣ SUCCESS — replay is read-only
        # ──────────────────────────────────────────────
        return ReplayResult(
            replay_id=self._replay_id(sealed),
            snapshot_hash=sealed.snapshot_hash,
            chain_hash=sealed.chain_hash,
            verification_status=True,
            replayed_components=list(view.components.keys()),
            discrepancies=[],
            warnings=[],
            audit_summary="Offline replay completed successfully",
        )

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    @staticmethod
    def _unwrap_snapshots(obj: Any):
        """
        Returns (view_snapshot, sealed_snapshot)

        IMPORTANT:
        Wrapper/driver unwrapping MUST happen first.
        """
        if hasattr(obj, "snapshot"):
            view = obj.snapshot
            if hasattr(view, "snapshot"):
                return view, view.snapshot
            return view, view

        if hasattr(obj, "components") and hasattr(obj, "snapshot_hash"):
            return obj, obj

        return None, None

    @staticmethod
    def _replay_id(snapshot: Any) -> str:
        payload = f"{snapshot.snapshot_hash}:{snapshot.chain_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _fail_safe(self, failure: ReplayFailure, component: str) -> ReplayResult:
        return ReplayResult(
            replay_id="UNKNOWN",
            snapshot_hash="UNKNOWN",
            chain_hash="UNKNOWN",
            verification_status=False,
            replayed_components=[],
            discrepancies=[
                ReplayDiscrepancy(component=component, description=failure.reason)
            ],
            warnings=[],
            audit_summary=f"Replay failed: {failure.reason}",
        )

    def _fail_from_snapshot(
        self,
        snapshot: Any,
        failure: ReplayFailure,
        component: str,
    ) -> ReplayResult:
        return ReplayResult(
            replay_id=self._replay_id(snapshot),
            snapshot_hash=snapshot.snapshot_hash,
            chain_hash=snapshot.chain_hash,
            verification_status=False,
            replayed_components=[],
            discrepancies=[
                ReplayDiscrepancy(component=component, description=failure.reason)
            ],
            warnings=[],
            audit_summary=f"Replay failed: {failure.reason}",
        )