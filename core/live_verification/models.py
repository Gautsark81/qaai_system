from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import hashlib
import json


# ----------------------------------------------------------
# Execution Trace Evidence (IMMUTABLE)
# ----------------------------------------------------------

@dataclass(frozen=True)
class ExecutionTraceEvidence:
    strategy_dna: str
    capital_decision_hash: str
    risk_verdict_hash: str
    execution_intent_hash: str
    router_call_hash: str
    mode: str  # SHADOW | LIVE
    timestamp_utc: str

    def compute_chain_hash(self) -> str:
        payload = json.dumps(
            {
                "strategy_dna": self.strategy_dna,
                "capital_decision_hash": self.capital_decision_hash,
                "risk_verdict_hash": self.risk_verdict_hash,
                "execution_intent_hash": self.execution_intent_hash,
                "router_call_hash": self.router_call_hash,
                "mode": self.mode,
                "timestamp_utc": self.timestamp_utc,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()


# ----------------------------------------------------------
# Live Proof Artifact (IMMUTABLE)
# ----------------------------------------------------------

@dataclass(frozen=True)
class LiveProofArtifact:
    trace: ExecutionTraceEvidence
    chain_hash: str
    authority_validated: bool

    def fingerprint(self) -> str:
        payload = json.dumps(
            {
                "trace_hash": self.chain_hash,
                "authority_validated": self.authority_validated,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()