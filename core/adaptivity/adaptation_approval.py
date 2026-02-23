# core/adaptivity/adaptation_approval.py

import yaml
from pathlib import Path
from core.adaptivity.parameter_registry import ParameterRegistry
from core.observability.event_bus import EventBus


class AdaptationApproval:
    """
    Applies approved adaptations.
    """

    def __init__(self, registry: ParameterRegistry):
        self.registry = registry
        self.approvals = Path("data/adaptivity/approvals")
        self.approvals.mkdir(parents=True, exist_ok=True)

    def apply(self, approval_file: str):
        path = self.approvals / approval_file
        if not path.exists():
            raise RuntimeError("Approval file not found")

        data = yaml.safe_load(path.read_text())

        name = data["parameter"]
        new_value = data["approved_value"]
        approved_by = data["approved_by"]

        self.registry.update(name, new_value)

        EventBus.emit(
            event_type="ADAPTATION_APPLIED",
            payload={
                "parameter": name,
                "new_value": new_value,
                "approved_by": approved_by,
            },
        )
