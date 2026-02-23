from .dna import StrategyDNA


class StrategyRegistry:
    def __init__(self):
        self._store: dict[str, StrategyDNA] = {}

    def register(self, dna: StrategyDNA) -> None:
        fid = dna.fingerprint()
        if fid in self._store:
            return
        self._store[fid] = dna

    def all(self) -> list[StrategyDNA]:
        return list(self._store.values())
