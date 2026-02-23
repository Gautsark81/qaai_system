from core.institution.memory.models import OrgMemoryRecord
from core.institution.memory.store import OrgMemoryStore


def test_append_and_list_memory():
    store = OrgMemoryStore()

    record = OrgMemoryRecord(
        record_id="R1",
        portfolio_id="P1",
        category="governance",
        summary="Capital cap increased",
        details={"old": 1_000_000, "new": 1_500_000},
    )

    store.append(record=record)

    records = store.list_all()
    assert records == [record]


def test_list_by_portfolio():
    store = OrgMemoryStore()

    r1 = OrgMemoryRecord(
        record_id="R1",
        portfolio_id="P1",
        category="risk",
        summary="Risk limits adjusted",
        details={},
    )
    r2 = OrgMemoryRecord(
        record_id="R2",
        portfolio_id="P2",
        category="governance",
        summary="New portfolio created",
        details={},
    )

    store.append(record=r1)
    store.append(record=r2)

    p1_records = store.list_by_portfolio(portfolio_id="P1")
    assert p1_records == [r1]
