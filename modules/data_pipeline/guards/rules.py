def invalid_price(bar):
    return bar.close <= 0


def frozen_candle(bar, prev_bar):
    return bar.close == prev_bar.close and bar.volume == 0


def extreme_gap(bar, prev_bar, sigma):
    return abs(bar.close - prev_bar.close) > sigma
