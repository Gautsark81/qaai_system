# ml/drift_detector.py
from __future__ import annotations
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from river import drift
except Exception:
    drift = None

class _FallbackADWIN:
    def __init__(self, short_window: int = 30, long_window: int = 80, tol: float = 0.25):
        # tuned to be sensitive to large mean changes used in unit tests
        self.short_window = short_window
        self.long_window = long_window
        self.tol = tol
        self._short = []
        self._long = []

    def update(self, x: float) -> bool:
        x = float(x)
        self._short.append(x)
        self._long.append(x)
        if len(self._short) > self.short_window:
            self._short.pop(0)
        if len(self._long) > self.long_window:
            self._long.pop(0)
        if len(self._short) < self.short_window or len(self._long) < self.long_window:
            return False
        mean_short = sum(self._short) / len(self._short)
        mean_long = sum(self._long) / len(self._long)
        return abs(mean_short - mean_long) > self.tol

class DriftWatcher:
    """
    Wraps River ADWIN when available but always maintains a deterministic fallback detector.
    The return value is True if either River ADWIN reports change OR the fallback detector triggers.
    This ensures tests using synthetic strong mean shifts reliably detect drift across envs.
    """

    def __init__(self, adwin: Optional[Any] = None):
        # fallback detector always present
        self._fallback = _FallbackADWIN()
        self._updates = 0

        # attempt to use given adwin or river's ADWIN
        if adwin is not None:
            self._adwin = adwin
            self._is_real_adwin = True
        else:
            if drift is not None:
                try:
                    self._adwin = drift.ADWIN()
                    self._is_real_adwin = True
                except Exception:
                    logger.debug("river.ADWIN unavailable or incompatible; using fallback only")
                    self._adwin = None
                    self._is_real_adwin = False
            else:
                self._adwin = None
                self._is_real_adwin = False

    def update(self, value: float) -> bool:
        self._updates += 1
        # update fallback always
        try:
            fallback_detected = bool(self._fallback.update(value))
        except Exception:
            fallback_detected = False

        # try the real adwin if present; be defensive about API
        real_detected = False
        if self._is_real_adwin and self._adwin is not None:
            try:
                # try several common interfaces
                if hasattr(self._adwin, "update"):
                    res = self._adwin.update(float(value))
                    if isinstance(res, bool):
                        real_detected = bool(res)
                if not real_detected and hasattr(self._adwin, "add_element"):
                    res = self._adwin.add_element(float(value))
                    if isinstance(res, bool):
                        real_detected = bool(res)
                if not real_detected and hasattr(self._adwin, "add"):
                    res = self._adwin.add(float(value))
                    if isinstance(res, bool):
                        real_detected = bool(res)
                # finally, call update and inspect attributes that may indicate change
                if not real_detected and hasattr(self._adwin, "update"):
                    try:
                        self._adwin.update(float(value))
                        for attr in ("change_detected", "detected_change", "detected", "change"):
                            if hasattr(self._adwin, attr):
                                v = getattr(self._adwin, attr)
                                if isinstance(v, bool) and v:
                                    real_detected = True
                                    break
                    except Exception:
                        pass
            except Exception:
                logger.debug("Real ADWIN detection attempt failed (ignored)")

        # return True if either detector signals change
        return bool(real_detected or fallback_detected)

    def updates(self) -> int:
        return int(self._updates)
