from dataclasses import dataclass
from hashlib import sha256
from .axes import *


@dataclass(frozen=True)
class StrategyDNA:
    structure: MarketStructure
    regime: RegimeState
    transition: RegimeTransition
    liquidity: LiquidityModel
    efficiency: EfficiencyState
    session: SessionState
    entry: EntryType
    risk: RiskShape
    exit: ExitIntent
    role: PortfolioRole

    def fingerprint(self) -> str:
        payload = "|".join(
            [
                self.structure.value,
                self.regime.value,
                self.transition.value,
                self.liquidity.value,
                self.efficiency.value,
                self.session.value,
                self.entry.value,
                self.risk.value,
                self.exit.value,
                self.role.value,
            ]
        )
        return sha256(payload.encode()).hexdigest()
