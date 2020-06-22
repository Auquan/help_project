"""
Test economic model
"""
from help_project.src.exitstrategies import lockdown_policy
from help_project.src.economic_model.models.basic_lockdown_model import EconomicLockdownModel


def test_economic_model():
    """
    test for economic_model
    """
    policy = lockdown_policy.LockdownPolicy(
        agriculture=0.2,
        chemical=0.2,
        commerce=0.2,
        construction=0.2,
        education=0.2,
        fin_prof_services=0.2,
    )
    economic_vector = EconomicLockdownModel().get_economic_vector(lockdown_policy=policy)
    assert len(economic_vector.keys()) > 0
