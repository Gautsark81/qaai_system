class PositionAlertPolicy:
    """
    Determines if position drift must alert.
    """

    @staticmethod
    def should_alert(matched: bool) -> bool:
        return not matched
