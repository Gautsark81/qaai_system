# core/governance/integrity/governance_ledger_fingerprint_engine.py

import hashlib
import json
from typing import Any


class GovernanceLedgerFingerprintEngine:
    """
    Phase C6.3

    Deterministic fingerprint of ledger state.

    Input:
    - scaling ledger
    - throttle ledger
    - capital usage ledger

    Guarantees:
    - Order independent
    - Deterministic
    - No mutation
    """

    @staticmethod
    def compute_fingerprint(*, ledgers: Any) -> str:
        normalized = GovernanceLedgerFingerprintEngine._normalize(ledgers)

        canonical = json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                key: GovernanceLedgerFingerprintEngine._normalize(obj[key])
                for key in sorted(obj.keys())
            }

        if isinstance(obj, list):
            # sort entries deterministically by their JSON string
            normalized_list = [
                GovernanceLedgerFingerprintEngine._normalize(x) for x in obj
            ]
            return sorted(normalized_list, key=lambda x: json.dumps(x, sort_keys=True))

        return obj