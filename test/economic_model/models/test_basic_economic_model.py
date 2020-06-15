"""
Test economic model
"""

from help_project.src.economic_model.models.basic_lockdown_model import EconomicLockdownModel


def test_economic_model():
    """
    test for economic_model
    """
    economic_output = False
    lockdown_vector = {
        "agriculture" : 0.2,
        "chemical" :  0.2,
        "commerce": 0.2,
        "construction": 0.2,
        "education": 0.2,
        "fin_prof_services":0.2,
        }
    economic_vector = EconomicLockdownModel(lockdown_vector=lockdown_vector).get_economic_vector()
    if len(economic_vector.keys()) > 0:
        economic_output = True

    assert economic_output
