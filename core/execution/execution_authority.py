# core/execution/execution_authority.py

from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Optional


# ---------------------------------------------------------------------
# Authority State (Immutable Snapshot)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class AuthorityState:
    frozen: bool
    safe_mode: bool
    reason: Optional[str]


# ---------------------------------------------------------------------
# Execution Authority
# ---------------------------------------------------------------------

class ExecutionAuthority:
    """
    Institutional Execution Authority.

    Responsibilities:
    - Centralize freeze decisions
    - Maintain safe-mode state
    - Preserve first freeze reason (idempotent)
    - Block execution when frozen
    - Allow manual clear by operator

    Properties:
    - Thread-safe
    - Deterministic
    - Freeze-first
    - Idempotent freeze
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._frozen: bool = False
        self._safe_mode: bool = False
        self._reason: Optional[str] = None

    # =============================================================
    # FREEZE
    # =============================================================

    def freeze(self, reason: str) -> None:
        """
        Freeze execution authority.
        First freeze reason persists (idempotent).
        """

        with self._lock:
            if self._frozen:
                # Preserve original reason
                return

            self._frozen = True
            self._safe_mode = True
            self._reason = reason

    # =============================================================
    # MANUAL CLEAR
    # =============================================================

    def manual_clear(self) -> None:
        """
        Operator-level reset of authority state.
        """

        with self._lock:
            self._frozen = False
            self._safe_mode = False
            self._reason = None

    # =============================================================
    # EXECUTION VALIDATION
    # =============================================================

    def validate_execution_allowed(self) -> bool:
        """
        Returns False if execution must be blocked.
        """

        with self._lock:
            return not self._frozen

    # =============================================================
    # STATE ACCESS
    # =============================================================

    def get_state(self) -> AuthorityState:
        """
        Returns immutable snapshot of authority state.
        """

        with self._lock:
            return AuthorityState(
                frozen=self._frozen,
                safe_mode=self._safe_mode,
                reason=self._reason,
            )