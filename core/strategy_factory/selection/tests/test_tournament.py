from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.selection.tournament import StrategyTournament


def test_tournament_runs():
    population = [ASTNode("price") for _ in range(10)]
    tournament = StrategyTournament(rounds=2)

    winners = tournament.run(population, survivors=3)
    assert len(winners) == 3
