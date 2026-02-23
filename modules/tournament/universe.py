class TradingUniverse:
    def __init__(self, symbols: list[str]):
        if len(symbols) < 50:
            raise ValueError("Universe too small for tournament")

        self.symbols = symbols
