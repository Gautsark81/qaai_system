import json
from typing import Optional, Dict, Any, Iterator


class ExplainabilityLogger:
    def __init__(self, filepath: Optional[str] = None):
        self.filepath = str(filepath) if filepath else None
        self._buffer = []

    def log(
        self,
        symbol: str,
        timestamp: str,
        features: Dict[str, Any],
        score: float,
        reason: str,
        rule_score: float = None,
        ml_score: float = None,
        feedback: float = None,
        final_score: float = None,
    ):
        """Log one screening decision with flat structure (test-compatible)."""
        entry = {
            "symbol": symbol,
            "timestamp": timestamp,
            "features": features,
            "score": score,
            "reason": reason,
        }
        # add optional fields only if provided
        if rule_score is not None:
            entry["rule_score"] = rule_score
        if ml_score is not None:
            entry["ml_score"] = ml_score
        if feedback is not None:
            entry["feedback"] = feedback
        if final_score is not None:
            entry["final_score"] = final_score

        self._buffer.append(entry)
        if self.filepath:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

    def read(self) -> Iterator[Dict[str, Any]]:
        """Iterate through stored log entries."""
        if self.filepath:
            with open(self.filepath, "r", encoding="utf-8") as f:
                for line in f:
                    yield json.loads(line)
        else:
            yield from self._buffer
