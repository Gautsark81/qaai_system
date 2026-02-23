class ReconciliationAlertPolicy:
    """
    Determines when reconciliation drift must alert.
    """

    @staticmethod
    def should_alert(within_tolerance: bool) -> bool:
        return not within_tolerance
