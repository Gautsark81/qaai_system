from core.explainability.causality.models import CausalChain, CausalNode
from core.explainability.summary.summarizer import HumanReadableSummarizer


def test_human_readable_summary_order_and_content():
    chain = CausalChain(
        chain_id="chain-1",
        nodes=[
            CausalNode(
                event_id="e1",
                description="Risk approved",
                evidence_ref={"risk_id": "R1"},
            ),
            CausalNode(
                event_id="e2",
                description="Trade executed",
                evidence_ref={"trade_id": "T1"},
            ),
        ],
    )

    summarizer = HumanReadableSummarizer()
    summary = summarizer.summarize(chain)

    assert summary == [
        "Step 1: Risk approved.",
        "Step 2: Trade executed.",
    ]
