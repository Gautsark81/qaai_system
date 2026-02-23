class CIInvariant:
    """
    Hard rules checked in CI.
    """

    @staticmethod
    def enforce(test_failures: int) -> bool:
        return test_failures == 0
