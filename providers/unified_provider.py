# providers/unified_provider.py
"""
UnifiedProvider: wrapper that chooses between paper and live provider,
and supports optional risk_manager enforcement.

Behavior:
 - exposes set_risk_manager
 - exposes set_mode / get_mode so callers can switch between "paper" and "live"
 - performs provider/rm checks when submit_order_with_retry(..., raise_on_risk=True)
 - if raise_on_risk=True and NO risk manager is attached (neither wrapper nor provider),
   the call will fail-closed.
"""

from typing import Any, Dict, Optional
import time


class UnifiedProvider:
    def __init__(
        self,
        paper_provider,
        live_provider=None,
        default_mode: str = "paper",
        logger=None,
        risk_manager: Optional[Any] = None,
    ):
        self.paper = paper_provider
        self.live = live_provider
        self.mode = default_mode
        self._logger = logger
        self.risk_manager = risk_manager

    # -------------------------
    # Mode and risk helpers
    # -------------------------
    def set_mode(self, mode: str) -> None:
        """
        Switch provider mode at runtime. Accepts "paper" or "live".
        If live provider is not present and 'live' requested, it will still set the mode
        (calls to submit will fall back to the paper provider via _active()).
        """
        try:
            mode_low = (mode or "").lower()
            if mode_low not in ("paper", "live"):
                raise ValueError("mode must be 'paper' or 'live'")
            self.mode = mode_low
        except Exception:
            # keep existing mode on invalid input
            if self._logger:
                try:
                    self._logger.warning(f"Ignoring invalid mode set request: {mode}")
                except Exception:
                    pass

    def get_mode(self) -> str:
        return self.mode

    def set_risk_manager(self, rm) -> None:
        self.risk_manager = rm

    def _active(self):
        if self.mode == "live" and self.live is not None:
            return self.live
        return self.paper

    # -------------------------
    # Connection / info methods
    # -------------------------
    def connect(self) -> bool:
        provider = self._active()
        try:
            if hasattr(provider, "connect"):
                return provider.connect()
            return True
        except Exception:
            return False

    def is_connected(self) -> bool:
        provider = self._active()
        try:
            if hasattr(provider, "is_connected"):
                return provider.is_connected()
            return bool(getattr(provider, "_connected", True))
        except Exception:
            return False

    def get_account_nav(self) -> Optional[float]:
        provider = self._active()
        try:
            if hasattr(provider, "get_account_nav"):
                return provider.get_account_nav()
            return float(getattr(provider, "_account_nav", 0.0))
        except Exception:
            return None

    def get_positions(self) -> Dict[str, Any]:
        provider = self._active()
        try:
            if hasattr(provider, "get_positions"):
                return provider.get_positions() or {}
            return dict(getattr(provider, "_positions", {}) or {})
        except Exception:
            return {}

    # -------------------------
    # Submission / retries
    # -------------------------
    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit directly through provider; enforce provider/risk checks here to avoid bypass.
        Provider-local RM preferred; wrapper RM acts as fallback.
        """
        provider = self._active()

        # Enforce provider-local risk manager first, then wrapper-level RM as fallback
        try:
            prov_rm = getattr(provider, "risk_manager", None)
            if prov_rm is not None:
                from utils.risk_utils import enforce_risk_or_raise

                enforce_risk_or_raise(prov_rm, provider, order)
            else:
                wrapper_rm = getattr(self, "risk_manager", None)
                if wrapper_rm is not None:
                    from utils.risk_utils import enforce_risk_or_raise

                    enforce_risk_or_raise(wrapper_rm, provider, order)
        except ValueError:
            # bubble up explicit denials
            raise
        except Exception:
            # non-fatal; log if possible
            if self._logger:
                try:
                    self._logger.debug(
                        "Risk enforcement in UnifiedProvider.submit_order failed (non-fatal)"
                    )
                except Exception:
                    pass

        # Delegate to provider
        if hasattr(provider, "submit_order"):
            return provider.submit_order(order)
        elif hasattr(provider, "submit"):
            return provider.submit(order)
        else:
            return {"status": "ERROR", "reason": "NO_SUBMIT_METHOD"}

    def submit_order_with_retry(
        self,
        order: Dict[str, Any],
        retries: int = 1,
        retry_delay: float = 0.0,
        raise_on_risk: bool = False,
    ):
        """
        If raise_on_risk=True, run risk enforcement prior to any submission attempts.
        Uses wrapper RM if present, otherwise provider-local RM.
        If raise_on_risk=True and NO risk manager exists anywhere, fail-closed.
        """
        provider = self._active()

        if raise_on_risk:
            # determine available RMs
            wrapper_rm = getattr(self, "risk_manager", None)
            prov_rm = getattr(provider, "risk_manager", None)

            # If no risk manager at all, fail closed (tests expect explicit denial)
            if wrapper_rm is None and prov_rm is None:
                raise ValueError("Trading not allowed")

            # If any RM exists, prefer wrapper RM then provider RM
            try:
                from utils.risk_utils import enforce_risk_or_raise

                if wrapper_rm is not None:
                    enforce_risk_or_raise(wrapper_rm, provider, order)
                elif prov_rm is not None:
                    enforce_risk_or_raise(prov_rm, provider, order)
            except ValueError:
                # explicit denial -> bubble up
                raise
            except Exception:
                if self._logger:
                    try:
                        self._logger.debug(
                            "Risk enforcement quick check failed (non-fatal) in submit_order_with_retry"
                        )
                    except Exception:
                        pass

        last = None
        for i in range(retries + 1):
            resp = self.submit_order(order)
            last = resp
            if resp and resp.get("status") not in ("ERROR",):
                return resp
            if i < retries:
                time.sleep(retry_delay)
        return last
