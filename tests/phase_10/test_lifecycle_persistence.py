from tempfile import TemporaryDirectory

from modules.strategy_lifecycle.persistence import FileBackedLifecycleStore
from modules.strategy_lifecycle.states import StrategyState


def test_lifecycle_state_persists_across_restarts():
    with TemporaryDirectory() as tmp:
        path = f"{tmp}/lifecycle.json"

        # --- first run
        store1 = FileBackedLifecycleStore(path=path)
        store1.set_state("s1", StrategyState.ACTIVE)
        store1.set_state("s2", StrategyState.DISABLED)

        assert store1.get_state("s1") == StrategyState.ACTIVE
        assert store1.get_state("s2") == StrategyState.DISABLED

        # --- simulate restart
        store2 = FileBackedLifecycleStore(path=path)

        assert store2.get_state("s1") == StrategyState.ACTIVE
        assert store2.get_state("s2") == StrategyState.DISABLED


def test_missing_file_starts_clean():
    with TemporaryDirectory() as tmp:
        path = f"{tmp}/missing.json"

        store = FileBackedLifecycleStore(path=path)

        assert store.get_state("unknown") == StrategyState.INIT
