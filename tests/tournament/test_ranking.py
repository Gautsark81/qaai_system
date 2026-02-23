from qaai_system.tournament.ranking import rank_strategies


def test_ranking_order():
    ranked = rank_strategies([
        ("A", 0.5),
        ("B", 1.2),
        ("C", 0.9),
    ])

    assert ranked[0][0] == "B"
