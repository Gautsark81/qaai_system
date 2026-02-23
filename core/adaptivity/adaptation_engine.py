# core/adaptivity/adaptation_engine.py

import json
from datetime import datetime
from pathlib import Path
from typing import Dict
from core.adaptivity.parameter_registry import ParameterRegistry
from core.observability.event_bus import EventBus


class AdaptationEngine:
    """
    Generates adaptation proposals (NO activation).
    """

    def __init__(self, registry: ParameterRegistry):
        self.registry = registry
        self.proposals_path = Path("data/adaptivity/proposals")
        self.proposals_path.mkdir(parents=True, exist_ok=True)

    def propose(
        self,
        parameter_name: str,
        proposed_value: float,
        reason: str,
        evidence: Dict,
    ) -> str:
        param = self.registry.get(parameter_name)
        param.validate(proposed_value)

        proposal_id = f"{parameter_name}_{datetime.utcnow().isoformat()}"
        payload = {
            "proposal_id": proposal_id,
            "parameter": parameter_name,
            "current_value": param.current_value,
            "proposed_value": proposed_value,
            "bounds": [param.min_value, param.max_value],
            "reason": reason,
            "evidence": evidence,
            "created_at": datetime.utcnow().isoformat(),
        }

        path = self.proposals_path / f"{proposal_id}.json"
        path.write_text(json.dumps(payload, indent=2))

        EventBus.emit(
            event_type="ADAPTATION_PROPOSED",
            payload=payload,
        )

        return proposal_id
