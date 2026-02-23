from core.screening.rule_types import RuleCategory


def test_rule_category_enum():
    assert RuleCategory.SANITY.value == "SANITY"
    assert RuleCategory.STRUCTURE.value == "STRUCTURE"
    assert RuleCategory.LIQUIDITY.value == "LIQUIDITY"
