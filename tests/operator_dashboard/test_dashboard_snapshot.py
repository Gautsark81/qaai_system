import json
from pathlib import Path

from modules.operator_dashboard.state_assembler import DashboardStateAssembler
from tests.operator_dashboard.utils import normalize

SNAPSHOT_PATH = Path(__file__).parent / "snapshots" / "dashboard_state.snapshot.json"


def test_dashboard_state_snapshot():
    state = DashboardStateAssembler.assemble()

    normalized = normalize(state)

    if not SNAPSHOT_PATH.exists():
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(
            json.dumps(normalized, indent=2),
            encoding="utf-8",
        )
        raise AssertionError(
            "Snapshot created. Review and re-run test."
        )

    expected = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert normalized == expected, (
        "Dashboard lifecycle snapshot changed.\n"
        "If intentional, update snapshot."
    )
