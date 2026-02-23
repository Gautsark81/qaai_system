from dataclasses import dataclass


@dataclass(frozen=True)
class SSRFlag:
    """
    Human-readable explanation for SSR degradation.
    """
    code: str
    severity: str      # LOW | MEDIUM | HIGH
    message: str
    component: str
