def rank_strategies(scored):
    """
    scored = [(snapshot, score)]
    Returns ranked list sorted by score desc
    """
    return sorted(scored, key=lambda x: x[1], reverse=True)
