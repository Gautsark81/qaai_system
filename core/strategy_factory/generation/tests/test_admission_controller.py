def test_admission_registers():
    from core.strategy_factory.generation.generator import generate_ast
    from core.strategy_factory.generation.admission import StrategyAdmissionController
    from core.strategy_factory.registry import StrategyRegistry

    registry = StrategyRegistry()
    admission = StrategyAdmissionController(registry)

    ast = generate_ast(1)
    record = admission.admit(ast)

    assert record.state == "GENERATED"
