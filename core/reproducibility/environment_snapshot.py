# core/reproducibility/environment_snapshot.py

from __future__ import annotations

import platform
import sys
import pkgutil
import json
from dataclasses import dataclass, asdict
from typing import Dict, List
from zoneinfo import ZoneInfo
from datetime import datetime


IST = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True)
class EnvironmentSnapshot:
    python_version: str
    platform_system: str
    platform_release: str
    machine: str
    processor: str
    timezone: str
    installed_packages: List[str]

    def to_canonical_dict(self) -> Dict:
        """
        Deterministic canonical representation.
        """
        return {
            "python_version": self.python_version,
            "platform_system": self.platform_system,
            "platform_release": self.platform_release,
            "machine": self.machine,
            "processor": self.processor,
            "timezone": self.timezone,
            "installed_packages": sorted(self.installed_packages),
        }

    def to_canonical_json(self) -> str:
        """
        Stable canonical JSON (sorted keys, no whitespace drift).
        """
        return json.dumps(
            self.to_canonical_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )


class EnvironmentSnapshotBuilder:
    """
    Deterministic environment snapshot builder.

    Read-only.
    No authority.
    """

    def build(self) -> EnvironmentSnapshot:
        packages = sorted(
            {module.name for module in pkgutil.iter_modules()}
        )

        return EnvironmentSnapshot(
            python_version=sys.version,
            platform_system=platform.system(),
            platform_release=platform.release(),
            machine=platform.machine(),
            processor=platform.processor(),
            timezone=str(IST),
            installed_packages=packages,
        )