from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalEnvelope:
    max_capital: float
    max_daily_loss: float


class CapitalEnvelopeValidator:
    def validate(
        self,
        requested_capital: float,
        envelope: CapitalEnvelope,
    ) -> bool:
        return requested_capital <= envelope.max_capital
