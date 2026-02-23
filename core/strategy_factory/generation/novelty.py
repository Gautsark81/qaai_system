# core/strategy_factory/generation/novelty.py

from core.strategy_factory.grammar.genome import Genome


class NoveltyFilter:
    def __init__(self):
        self._seen = set()

    def is_novel(self, ast) -> bool:
        fingerprint = Genome(ast).fingerprint()

        if fingerprint in self._seen:
            return False

        self._seen.add(fingerprint)
        return True
