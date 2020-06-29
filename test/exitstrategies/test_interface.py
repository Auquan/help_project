"""
Test for dummy lockdown vector
"""
import attr
from help_project.src.exitstrategies.interface import ExitStrategies


def test_strat_dict():
    # Generate strategies dictionary
    exit_strat = ExitStrategies()
    strat_dict = exit_strat.get_exit_strategies()

    assert len(strat_dict) > 0
    for strat_id in strat_dict:
        # Check for zero rows or columns
        strat = strat_dict[strat_id]
        assert len(strat.policies) > 0
        assert len(attr.asdict(strat[0])) > 0
