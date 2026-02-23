# core/dashboard_read/verification/verifier.py

from __future__ import annotations

from typing import Iterable, List

from core.dashboard_read.evidence.record import EvidenceRecord
from core.dashboard_read.crypto.snapshot_hash import compute_snapshot_hash
from core.dashboard_read.crypto.chain import (
    compute_chain_hash,
    GENESIS_CHAIN_HASH,
)
from core.dashboard_read.verification.report import (
    VerificationIssue,
    VerificationReport,
)


def verify_evidence_record(record: EvidenceRecord) -> VerificationReport:

    issues: List[VerificationIssue] = []

    expected_snapshot_hash = compute_snapshot_hash(record.snapshot)
    if expected_snapshot_hash != record.snapshot_hash:
        issues.append(
            VerificationIssue(
                code="SNAPSHOT_HASH_MISMATCH",
                message="Snapshot hash mismatch",
            )
        )

    expected_chain_hash = compute_chain_hash(
        record.snapshot_hash,
        record.previous_chain_hash,
    )

    if expected_chain_hash != record.chain_hash:
        issues.append(
            VerificationIssue(
                code="CHAIN_HASH_MISMATCH",
                message="Chain hash mismatch",
            )
        )

    if record.previous_chain_hash != GENESIS_CHAIN_HASH:
        issues.append(
            VerificationIssue(
                code="UNVERIFIED_LINEAGE",
                message="Non-genesis record must be verified in chain context",
            )
        )

    if issues:
        return VerificationReport.failure(issues)

    return VerificationReport.success()


def verify_evidence_chain(
    records: Iterable[EvidenceRecord],
) -> VerificationReport:

    records = list(records)
    issues: List[VerificationIssue] = []

    if not records:
        return VerificationReport.failure(
            [VerificationIssue(code="EMPTY_CHAIN", message="Empty chain")]
        )

    expected_previous = GENESIS_CHAIN_HASH

    for index, record in enumerate(records):

        expected_snapshot_hash = compute_snapshot_hash(record.snapshot)
        if expected_snapshot_hash != record.snapshot_hash:
            issues.append(
                VerificationIssue(
                    code=f"SNAPSHOT_HASH_MISMATCH@{index}",
                    message="Snapshot mismatch",
                )
            )

        if record.previous_chain_hash != expected_previous:
            issues.append(
                VerificationIssue(
                    code=f"CHAIN_LINK_BROKEN@{index}",
                    message="Parent linkage broken",
                )
            )

        expected_chain_hash = compute_chain_hash(
            record.snapshot_hash,
            expected_previous,
        )

        if expected_chain_hash != record.chain_hash:
            issues.append(
                VerificationIssue(
                    code=f"CHAIN_HASH_MISMATCH@{index}",
                    message="Chain hash mismatch",
                )
            )

        expected_previous = record.chain_hash

    if issues:
        return VerificationReport.failure(issues)

    return VerificationReport.success()