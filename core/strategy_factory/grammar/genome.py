import hashlib
import json
from dataclasses import dataclass
from .validator import validate
from .version import grammar_version
from .ast import ASTNode


@dataclass(frozen=True)
class Genome:
    ast: ASTNode

    def fingerprint(self) -> str:
        payload = {
            "grammar": grammar_version,
            "ast": self._serialize(self.ast),
        }
        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _serialize(self, node: ASTNode):
        return {
            "value": str(node.value),
            "children": [self._serialize(c) for c in node.children],
        }


@dataclass(frozen=True)
class StrategyGenome:
    version: str
    ast: ASTNode
    modifiers: list

    def fingerprint(self) -> str:
        return Genome(self.ast).fingerprint()
