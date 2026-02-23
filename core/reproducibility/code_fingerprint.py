# core/reproducibility/code_fingerprint.py

from __future__ import annotations
import subprocess
from dataclasses import dataclass
from datetime import datetime
import pytz

from .utils import sha256_string

IST = pytz.timezone("Asia/Kolkata")


@dataclass(frozen=True)
class CodeFingerprint:
    git_commit: str
    created_at: datetime

    @staticmethod
    def capture() -> "CodeFingerprint":
        try:
            commit = (
                subprocess.check_output(["git", "rev-parse", "HEAD"])
                .decode()
                .strip()
            )
        except Exception:
            raise RuntimeError("Git commit SHA not found. Git required.")

        return CodeFingerprint(
            git_commit=commit,
            created_at=datetime.now(IST),
        )

    def hash(self) -> str:
        return sha256_string(self.git_commit)