# core/reproducibility/environment_fingerprint.py

from __future__ import annotations
import platform
import subprocess
import sys
import pytz
from dataclasses import dataclass
from datetime import datetime

from .utils import sha256_json

IST = pytz.timezone("Asia/Kolkata")


@dataclass(frozen=True)
class EnvironmentFingerprint:
    python_version: str
    os: str
    architecture: str
    timezone: str
    dependency_hash: str
    created_at: datetime

    @staticmethod
    def capture() -> "EnvironmentFingerprint":

        pip_freeze = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"]
        ).decode()

        dependency_hash = sha256_json(pip_freeze.splitlines())

        return EnvironmentFingerprint(
            python_version=sys.version,
            os=platform.system(),
            architecture=platform.machine(),
            timezone="Asia/Kolkata",
            dependency_hash=dependency_hash,
            created_at=datetime.now(IST),
        )