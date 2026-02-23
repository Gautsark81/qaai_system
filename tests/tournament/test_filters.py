from qaai_system.tournament.filters import apply_hard_filters


def test_filter_rejects_low_ssr(dummy_snapshot):
    dummy_snapshot.ssr = 0.60

    survivors, eliminated = apply_hard_filters([dummy_snapshot])

    assert not survivors
    assert eliminated[0][1] == "SSR_BELOW_THRESHOLD"
