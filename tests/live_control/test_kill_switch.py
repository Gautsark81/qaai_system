from modules.live_control.kill_switch import KillSwitch


def test_global_kill_switch_blocks_all():
    ks = KillSwitch()
    ks.activate_global()

    assert ks.is_blocked(symbol="NIFTY", strategy_id="s1")


def test_symbol_blocking():
    ks = KillSwitch()
    ks.block_symbol("BANKNIFTY")

    assert ks.is_blocked(symbol="BANKNIFTY", strategy_id="s1")
    assert not ks.is_blocked(symbol="NIFTY", strategy_id="s1")


def test_strategy_blocking():
    ks = KillSwitch()
    ks.block_strategy("s1")

    assert ks.is_blocked(symbol="NIFTY", strategy_id="s1")
    assert not ks.is_blocked(symbol="NIFTY", strategy_id="s2")
