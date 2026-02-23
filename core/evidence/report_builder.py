# core/evidence/report_builder.py

"""
⚠️ LEGACY REPORT BUILDER

Uses local deterministic hashing.
Does NOT use Phase-F checksum engine.
"""

from datetime import datetime
from typing import Iterable, Any
import hashlib
import json

from core.evidence.report_contracts import ReplayAuditReport
from core.evidence.replay_contracts import ReplayFrame


def _freeze(value: Any):
    if isinstance(value, dict):
        return {k: _freeze(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [_freeze(v) for v in value]
    return value


def _legacy_checksum(payload: Any) -> str:
    """
    Deterministic legacy checksum (isolated from Phase-F engine).
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_audit_report(
    *,
    frames: Iterable[ReplayFrame],
) -> ReplayAuditReport:
    frames = list(frames)
    if not frames:
        raise ValueError("frames must not be empty")

    # --------------------------------------------------
    # 🔒 Deterministic timestamps (CRITICAL FIX)
    # --------------------------------------------------

    first, last = frames[0], frames[-1]

    generated_at = last.timestamp  # ← deterministic, evidence-derived

    # --------------------------------------------------
    # Frame snapshots
    # --------------------------------------------------

    frames_before = {
        "capital": first.capital_allocations,
        "governance": first.governance_states,
    }

    frames_after = {
        "capital": last.capital_allocations,
        "governance": last.governance_states,
    }

    diffs = {
        "capital_delta": {
            k: frames_after["capital"].get(k, 0.0)
            - frames_before["capital"].get(k, 0.0)
            for k in set(frames_before["capital"]) | set(frames_after["capital"])
        }
    }

    # --------------------------------------------------
    # 🔐 Deterministic checksum
    # --------------------------------------------------

    checksum_payload = _freeze(
        {
            "frames_before": frames_before,
            "frames_after": frames_after,
            "diffs": diffs,
        }
    )

    checksum = _legacy_checksum(checksum_payload)

    # --------------------------------------------------
    # Final immutable audit report
    # --------------------------------------------------

    return ReplayAuditReport(
        generated_at=generated_at,
        from_timestamp=first.timestamp,
        to_timestamp=last.timestamp,
        summary={"frames": len(frames)},
        frames_before=frames_before,
        frames_after=frames_after,
        diffs=diffs,
        evidence_count=len(frames),
        checksum=checksum,
    )
