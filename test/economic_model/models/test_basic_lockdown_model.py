"""
Test economic model
"""
import datetime
from help_project.src.exitstrategies import lockdown_policy
from help_project.src.economic_model.models.basic_lockdown_model import EconomicLockdownModel


def test_economic_model():
    """
    test for economic_model
    """
    policy_timeseries = lockdown_policy.LockdownTimeSeries(
        policies=[
            lockdown_policy.LockdownPolicyApplication(
                lockdown_policy.LockdownPolicy(
                    agriculture=0.2,
                    chemical=0.2,
                    commerce=0.2,
                    construction=0.2,
                    education=0.2,
                    fin_prof_services=0.2,
                ),
                start=datetime.date(2020, 1, 1),
                end=datetime.date(2020, 1, 10),
            ),
        ])
    economic_vector = EconomicLockdownModel().get_economic_vector(lockdown_policy=policy_timeseries)
    assert len(economic_vector.keys()) > 0
