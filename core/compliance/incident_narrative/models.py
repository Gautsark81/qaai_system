from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass(frozen=True)
class NarrativeSection:
    title: str
    content: str


@dataclass(frozen=True)
class IncidentNarrative:
    summary: str
    sections: List[NarrativeSection]

    def as_text(self) -> str:
        lines = [self.summary, ""]
        for s in self.sections:
            lines.append(f"## {s.title}")
            lines.append(s.content)
            lines.append("")
        return "\n".join(lines).strip()
