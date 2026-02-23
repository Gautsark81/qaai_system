from dataclasses import dataclass


@dataclass(frozen=True)
class PromotionPermissions:
    allow_live: bool
    allow_paper: bool
    reason: str
