from dataclasses import dataclass
from typing import Optional

from core.execution.replay.models import ReplayIdentity
from core.execution.replay.inputs import ReplayInputs
from core.execution.replay.results import ReplayResult


@dataclass(frozen=True)
class ReplayEnvelope:
    """
    Full replay artifact.
    """
    identity: ReplayIdentity
    inputs: ReplayInputs
    result: Optional[ReplayResult] = None
