from modules.tournament.leaderboard import Leaderboard, LeaderboardEntry


def test_leaderboard_sorting():
    lb = Leaderboard()
    ranked = lb.rank([
        LeaderboardEntry("s1", 0.7, 1000),
        LeaderboardEntry("s2", 0.85, 500),
        LeaderboardEntry("s3", 0.85, 1500),
    ])

    assert ranked[0].strategy_id == "s3"
