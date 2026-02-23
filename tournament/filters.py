MIN_TRADES = 30
MAX_DRAWDOWN = 0.25
MIN_SSR = 0.80


def apply_hard_filters(snapshots):
    """
    Returns (survivors, eliminated)
    eliminated = [(snapshot, reason)]
    """
    survivors = []
    eliminated = []

    for snap in snapshots:
        if snap.total_trades < MIN_TRADES:
            eliminated.append((snap, "INSUFFICIENT_TRADES"))
            continue

        if snap.ssr < MIN_SSR:
            eliminated.append((snap, "SSR_BELOW_THRESHOLD"))
            continue

        if snap.max_drawdown > MAX_DRAWDOWN:
            eliminated.append((snap, "DRAWDOWN_EXCEEDED"))
            continue

        if snap.risk_blocks > 0:
            eliminated.append((snap, "RISK_BLOCKS_PRESENT"))
            continue

        survivors.append(snap)

    return survivors, eliminated
