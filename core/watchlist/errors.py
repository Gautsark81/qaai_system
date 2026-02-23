class WatchlistViolation(Exception):
    """
    Raised when a trade attempts to proceed
    for a symbol not present in the active watchlist.
    This is a HARD invariant violation.
    """
    pass
