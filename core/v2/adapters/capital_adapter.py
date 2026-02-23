class CapitalAlphaAdapter:
    """
    Capital is ADVISORY ONLY in v2.

    v2 can observe capital approval,
    but can NEVER allocate, override, or mutate.
    """

    def allow_alpha(self, capital_approved: bool) -> str:
        if capital_approved:
            return "CAPITAL_OK"
        return "CAPITAL_BLOCKED"
