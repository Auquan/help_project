"""
Test economic model
"""

from help_project.src.economic_model.models.basic_lockdown_model import EconomicLockdownModel


def test_economic_model():
    """
    test for economic_model
    """
    economic_output = False
    economic_vector = EconomicLockdownModel().get_economic_vector()
    if len(economic_vector.keys()) > 0:
        economic_output = True

    assert economic_output
