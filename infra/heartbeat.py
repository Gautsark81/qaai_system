# infra/heartbeat.py
"""
Heartbeat helper to probe provider connectivity. This is synchronous and controllable
— not a background thread. Call check_and_reconnect() on intervals from your runner or tests.
"""

import time


class Heartbeat:
    def __init__(
        self,
        provider,
        reconnect_attempts: int = 1,
        reconnect_backoff: float = 0.0,
        logger=None,
    ):
        self.provider = provider
        self.reconnect_attempts = int(reconnect_attempts or 1)
        self.reconnect_backoff = float(reconnect_backoff or 0.0)
        self._logger = logger

    def check_and_reconnect(self) -> bool:
        """
        Return True if provider is connected after check; otherwise try reconnect attempts and return final status.
        """
        try:
            ok = self.provider.is_connected()
        except Exception:
            ok = False
        if ok:
            return True
        # attempt reconnect
        for i in range(self.reconnect_attempts):
            try:
                self.provider.connect()
            except Exception:
                pass
            try:
                if self.provider.is_connected():
                    return True
            except Exception:
                pass
            if i < self.reconnect_attempts - 1 and self.reconnect_backoff > 0:
                time.sleep(self.reconnect_backoff)
        return False
