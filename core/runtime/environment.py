# core/runtime/environment.py
import os
from dataclasses import dataclass
from typing import Optional

VALID_ENVS = {"dev", "staging", "prod", "test"}


@dataclass(frozen=True)
class RuntimeEnvironment:
    """
    Immutable runtime environment descriptor.

    Governance flags:
    - allow_live_execution: capital movement
    - allow_red_team: observability & fault injection (NO execution)
    """

    name: str
    allow_live_execution: bool = False
    allow_red_team: bool = False

    def __init__(
        self,
        name: Optional[str] = None,
        allow_live_execution: bool = False,
        *,
        mode: Optional[str] = None,
    ):
        # Support both RuntimeEnvironment("dev") and RuntimeEnvironment(mode="dev")
        env = mode if mode is not None else name

        if not env:
            raise ValueError("Runtime environment must be specified")

        env = env.lower().strip()

        if env not in VALID_ENVS:
            raise ValueError(f"Invalid runtime environment: {env}")

        object.__setattr__(self, "name", env)

        # Live execution is ONLY allowed in prod and only if explicitly enabled
        live_allowed = bool(allow_live_execution and env == "prod")
        object.__setattr__(self, "allow_live_execution", live_allowed)

        # Red-team observability is ONLY allowed in test
        object.__setattr__(self, "allow_red_team", env == "test")


def load_environment() -> RuntimeEnvironment:
    """
    Canonical production bootstrap from QAAI_ENV.
    """
    env = os.getenv("QAAI_ENV")

    if not env:
        raise RuntimeError("QAAI_ENV is not set")

    return RuntimeEnvironment(
        name=env,
        allow_live_execution=(env.lower().strip() == "prod"),
    )
