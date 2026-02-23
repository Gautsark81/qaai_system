class BaseReRanker:
    """
    Abstract façade for re-ranking.
    Core logic lives in core.watchlist.
    """

    def rerank(self, items):
        return items
