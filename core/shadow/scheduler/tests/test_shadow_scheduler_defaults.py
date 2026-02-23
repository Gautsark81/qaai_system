import pytest

from core.shadow.scheduler.scheduler import ShadowScheduler
from core.shadow.scheduler.config import ShadowSchedulerConfig


def test_shadow_scheduler_disabled_by_default():
    scheduler = ShadowScheduler()
    assert scheduler.is_enabled is False


def test_shadow_scheduler_requires_explicit_enable():
    config = ShadowSchedulerConfig()
    scheduler = ShadowScheduler(config=config)

    assert scheduler.is_enabled is False


def test_shadow_scheduler_enables_only_with_flag():
    config = ShadowSchedulerConfig(enable_shadow_scheduler=True)
    scheduler = ShadowScheduler(config=config)

    assert scheduler.is_enabled is True
