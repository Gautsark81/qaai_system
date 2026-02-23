from qaai_system.capital.weighting import compute_weight
from qaai_system.capital.decay import apply_decay
from qaai_system.capital.caps import apply_caps
from qaai_system.capital.correlation import apply_correlation_penalty


class CapitalAllocator:
    def allocate(
        self,
        *,
        snapshot,
        correlated: bool,
    ):
        # 1️⃣ Base weight
        weight = compute_weight(snapshot)

        # 2️⃣ Decay
        weight, status, reason = apply_decay(weight, snapshot)

        # 3️⃣ Caps
        weight = apply_caps(weight)

        # 4️⃣ Correlation throttle
        weight = apply_correlation_penalty(weight, correlated)

        return weight, status, reason
