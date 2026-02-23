def read_market_regime():
    """
    Read current market regime.

    Tests will monkeypatch this.
    """
    raise RuntimeError("Market regime source not wired")


def read_extreme_event_state():
    """
    Read extreme / crash state.

    Tests will monkeypatch this.
    """
    raise RuntimeError("Extreme event source not wired")


def read_market_session():
    """
    Read market session state (open / closed / halt).

    Tests will monkeypatch this.
    """
    raise RuntimeError("Market session source not wired")
