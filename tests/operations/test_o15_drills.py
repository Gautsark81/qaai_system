from datetime import datetime

from core.operations.drills.drill_contract import OpsDrill
from core.operations.drills.drill_runner import OpsDrillRunner
from core.operations.drills.drill_replay import DrillReplayValidator
from core.operations.ops_store import OpsEventStore


def test_o15_kill_switch_drill(tmp_path):
    ops = OpsEventStore(root_dir=tmp_path)

    drill = OpsDrill(
        drill_id="drill_001",
        drill_type="kill_switch",
        target="system",
        initiated_by="operator_1",
        initiated_at=datetime.utcnow(),
        expected_response="Trading halted immediately",
    )

    OpsDrillRunner(ops).run(drill)

    drills = DrillReplayValidator(ops).list_drills()

    assert len(drills) == 1
    assert "kill_switch" in drills[0]["event_type"]
