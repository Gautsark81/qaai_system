class KillSwitch:
    """
    Global emergency kill-switch.
    """

    def __init__(self):
        self._armed = False

    def arm(self):
        self._armed = True

    def disarm(self):
        self._armed = False

    def assert_not_armed(self):
        if self._armed:
            raise RuntimeError(
                "Global kill-switch is armed"
            )
