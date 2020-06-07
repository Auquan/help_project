"""
Test economic model
"""

from src.economic_model.models.basic_lockdown_model import EconomicLockdownModel


def test_economic_model():
    """
    test for economic_model
    """
    lockdown_output = False

    try:
        economic_vector = EconomicLockdownModel().get_economic_vector()
        if len(economic_vector.keys()) > 0:
            lockdown_output = True
    except Exception as excep:
        print("economic model not working:\n", excep)

    assert lockdown_output
