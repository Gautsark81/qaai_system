"""
TEST-ONLY adapter for Phase 20 red-team replay.

This file intentionally lives under tests/.
It exposes a controlled execution surface for RedTeamReplayDriver
without modifying production replay code.
"""

class RedTeamReplayAdapter:
    def __init__(self, driver):
        self._driver = driver

    def run(self, *, ticks, regime_events):
        """
        Drive replay using the internal protocol already supported
        by the system runtime.
        """
        # The driver already has access to system_runtime via fixture wiring.
        # We inject events through the canonical channels it listens to.
        self._driver.inject_ticks(ticks)
        self._driver.inject_regime_events(regime_events)
        self._driver.advance_until_complete()
