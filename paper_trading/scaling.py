class ScaleManager:
    """
    Converts signal strength [0..1] into a size multiplier.
    Safe range: [min_scale, max_scale].
    """

    def __init__(self, min_scale: float = 0.5, max_scale: float = 2.0):
        self.min_scale = min_scale
        self.max_scale = max_scale

    def multiplier(self, strength: float) -> float:
        s = max(0.0, min(1.0, float(strength)))
        return self.min_scale + s * (self.max_scale - self.min_scale)
