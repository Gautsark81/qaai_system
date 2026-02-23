from qaai_system.execution import ExecutionFlags, ExecutionMode


def test_default_mode_is_dry_run():
    flags = ExecutionFlags()
    assert flags.mode() == ExecutionMode.DRY_RUN


def test_can_switch_to_live():
    flags = ExecutionFlags()
    flags.set_mode(ExecutionMode.LIVE)
    assert flags.is_live() is True
