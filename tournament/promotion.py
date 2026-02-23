def select_top_k(results, k: int):
    """
    Select top-K eligible strategies.
    """
    return [r for r in results if r.eligible][:k]
