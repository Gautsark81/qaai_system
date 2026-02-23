from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ASTNode:
    value: Any
    children: Optional[List["ASTNode"]] = field(default_factory=list)

    # ---- Compatibility Alias (Required by Tests & DSL) ----
    @property
    def node(self) -> Any:
        return self.value

    def depth(self) -> int:
        if not self.children:
            return 1
        return 1 + max(child.depth() for child in self.children)

    def node_count(self) -> int:
        if not self.children:
            return 1
        return 1 + sum(child.node_count() for child in self.children)
