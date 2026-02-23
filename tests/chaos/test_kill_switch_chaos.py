from modules.live_control.kill_switch import KillSwitch

def test_global_kill_switch_blocks_everything():
    ks = KillSwitch()
    ks.activate_global()

    for symbol in ["NIFTY", "BANKNIFTY"]:
        for sid in ["s1", "s2"]:
            assert ks.is_blocked(symbol=symbol, strategy_id=sid)
