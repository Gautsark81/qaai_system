from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class SystemHealthSnapshot:
    timestamp: datetime
    components: Dict[str, str]   # component -> status
    warnings: int
    errors: int
