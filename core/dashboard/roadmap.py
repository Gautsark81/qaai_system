# File: core/dashboard/roadmap.py
#
# Canonical roadmap registry for QAAI_SYSTEM.
# This is a READ-ONLY visibility contract.
# It does NOT drive execution, intelligence, or governance.

from typing import List, Dict


_ALLOWED_STATUS = {
    "LOCKED",
    "COMPLETE",
    "IN_PROGRESS",
    "PARTIAL",
    "PENDING",
    "BLOCKED",
}


def get_full_roadmap() -> List[Dict]:
    """
    Returns the full locked roadmap in strict phase order.
    This is the single source of truth for dashboard rendering.
    """

    roadmap = [
        {
            "phase_id": "PHASE_0",
            "order": 0,
            "name": "Foundation & Core Infra",
            "status": "COMPLETE",
            "locked": True,
            "visible": True,
            "sub_phases": [
                {"id": "0.1", "description": "Project scaffolding, env isolation", "status": "COMPLETE"},
                {"id": "0.2", "description": "Config, secrets, dependency hygiene", "status": "COMPLETE"},
                {"id": "0.3", "description": "Logging, deterministic seeds", "status": "COMPLETE"},
                {"id": "0.4", "description": "Core utilities & contracts", "status": "COMPLETE"},
            ],
        },
        {
            "phase_id": "PHASE_1",
            "order": 1,
            "name": "Snapshot, Execution & Safety Core",
            "status": "COMPLETE",
            "locked": True,
            "visible": True,
            "sub_phases": [
                {"id": "1.1", "description": "Snapshot identity & hashing", "status": "COMPLETE"},
                {"id": "1.2", "description": "Snapshot immutability contract", "status": "COMPLETE"},
                {"id": "1.3", "description": "Execution state capture", "status": "COMPLETE"},
                {"id": "1.4", "description": "Snapshot promotion & lineage", "status": "COMPLETE"},
                {"id": "1.5", "description": "Safety flags & arming model", "status": "COMPLETE"},
                {"id": "1.6", "description": "Execution gating", "status": "COMPLETE"},
                {"id": "1.7", "description": "Governance state embedding", "status": "COMPLETE"},
                {"id": "1.8", "description": "Execution decision isolation", "status": "COMPLETE"},
                {"id": "1.9", "description": "Execution arming lifecycle", "status": "COMPLETE"},
            ],
        },
        {
            "phase_id": "PHASE_2",
            "order": 2,
            "name": "Governance & Operator Records",
            "status": "COMPLETE",
            "locked": True,
            "visible": True,
            "sub_phases": [
                {"id": "2.1", "description": "Governance evaluation rules", "status": "COMPLETE"},
                {"id": "2.2", "description": "Governance decision records", "status": "COMPLETE"},
                {"id": "2.3", "description": "Operator acknowledgement records", "status": "COMPLETE"},
                {"id": "2.4", "description": "Decision drift analytics", "status": "COMPLETE"},
            ],
        },
        {
            "phase_id": "PHASE_3",
            "order": 3,
            "name": "Adaptive Context (Descriptive Only)",
            "status": "COMPLETE",
            "locked": True,
            "visible": True,
            "sub_phases": [
                {"id": "3.0", "description": "Adaptive context surface", "status": "COMPLETE"},
            ],
        },
        {
            "phase_id": "PHASE_4",
            "order": 4,
            "name": "Capital & Throttling Governance",
            "status": "COMPLETE",
            "locked": True,
            "visible": True,
            "sub_phases": [
                {"id": "4.1", "description": "Capital throttling contracts", "status": "COMPLETE"},
                {"id": "4.2", "description": "Capital governance rules", "status": "COMPLETE"},
                {"id": "4.3", "description": "Capital throttle audit events", "status": "COMPLETE"},
                {"id": "4.4", "description": "Capital usage ledger", "status": "COMPLETE"},
            ],
        },
        {
            "phase_id": "PHASE_5",
            "order": 5,
            "name": "Strategy Factory & Lifecycle",
            "status": "COMPLETE",
            "locked": True,
            "visible": True,
            "sub_phases": [
                {"id": "5.1", "description": "Strategy factory contracts", "status": "COMPLETE"},
                {"id": "5.2", "description": "Strategy identity (DNA)", "status": "COMPLETE"},
                {"id": "5.3", "description": "Strategy lifecycle states", "status": "COMPLETE"},
                {"id": "5.4", "description": "Promotion & demotion hooks", "status": "COMPLETE"},
            ],
        },
        {
            "phase_id": "PHASE_6",
            "order": 6,
            "name": "Execution, Idempotency & Recovery",
            "status": "COMPLETE",
            "locked": True,
            "visible": True,
            "sub_phases": [
                {"id": "6.1", "description": "Order routing abstraction", "status": "COMPLETE"},
                {"id": "6.2", "description": "Execution idempotency", "status": "COMPLETE"},
                {"id": "6.3", "description": "Restart recovery", "status": "COMPLETE"},
                {"id": "6.4", "description": "Reconciliation logic", "status": "COMPLETE"},
            ],
        },
        {
            "phase_id": "PHASE_7",
            "order": 7,
            "name": "Observability & Evidence",
            "status": "COMPLETE",
            "locked": True,
            "visible": True,
            "sub_phases": [
                {"id": "7.1", "description": "Evidence models", "status": "COMPLETE"},
                {"id": "7.2", "description": "Event journaling", "status": "COMPLETE"},
                {"id": "7.3", "description": "Operator visibility", "status": "COMPLETE"},
            ],
        },
        {
            "phase_id": "PHASE_8",
            "order": 8,
            "name": "Operator & Forensic Plane",
            "status": "COMPLETE",
            "locked": True,
            "visible": True,
            "sub_phases": [
                {"id": "8.1", "description": "Operator read-only surface", "status": "COMPLETE"},
                {"id": "8.2", "description": "Operator audit surface", "status": "COMPLETE"},
                {"id": "8.3", "description": "Audit lineage trace", "status": "COMPLETE"},
                {"id": "8.4", "description": "Forensic replay surface", "status": "COMPLETE"},
            ],
        },
        {
            "phase_id": "PHASE_9",
            "order": 9,
            "name": "Strategy Intelligence",
            "status": "PENDING",
            "locked": False,
            "visible": True,
            "sub_phases": [],
        },
    ]

    # Defensive validation
    for phase in roadmap:
        if phase["status"] not in _ALLOWED_STATUS:
            raise ValueError(f"Invalid roadmap status: {phase}")

    return roadmap
