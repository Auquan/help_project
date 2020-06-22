"""Tests for the lockdown_policy module."""
import datetime
import pytest
import attr
from help_project.src.exitstrategies import lockdown_policy


def test_lockdown_policy_initialization_from_dict():
    """Test LockdownPolicy attributes get correctly initialized from a dict."""
    policy = lockdown_policy.LockdownPolicy(**{'agriculture': 0.5})
    assert policy.agriculture == 0.5
    assert policy.air_travel == 0.0


def test_lockdown_policy_initialization_from_kwargs():
    """Test LockdownPolicy attributes get correctly initialized from keyword args."""
    policy = lockdown_policy.LockdownPolicy(agriculture=0.5)
    assert policy.agriculture == 0.5
    assert policy.air_travel == 0.0


def test_lockdown_policy_immutable():
    """Test LockdownPolicy attributes cannot be modified."""
    policy = lockdown_policy.LockdownPolicy(agriculture=0.5)
    with pytest.raises(attr.exceptions.FrozenInstanceError):
        policy.agriculture = 0.2


def test_lockdown_policy_behavior_in_set():
    """Test LockdownPolicy can be put into a set as expected."""
    policy1 = lockdown_policy.LockdownPolicy(agriculture=0.2)
    policy2 = lockdown_policy.LockdownPolicy(agriculture=0.3)
    assert len({policy1, policy2}) == 2

    policy2_clone = lockdown_policy.LockdownPolicy(agriculture=0.3)
    assert len({policy2, policy2_clone}) == 1


def test_lockdown_policy_application_length():
    """Test LockdownPolicyApplication length works as expected."""
    policy_app = lockdown_policy.LockdownPolicyApplication(
        policy=lockdown_policy.LockdownPolicy(agriculture=0.2),
        start=datetime.date(2020, 1, 10),
        end=datetime.date(2020, 1, 20),
    )
    assert len(policy_app) == 10


def test_lockdown_policy_application_length_when_end_not_set():
    """Test LockdownPolicyApplication length default when end is not set."""
    policy_app = lockdown_policy.LockdownPolicyApplication(
        policy=lockdown_policy.LockdownPolicy(agriculture=0.2),
        start=datetime.date(2020, 1, 10),
        end=None,
    )
    assert len(policy_app) == 365


def test_lockdown_policy_timeseries_indexable_with_int():
    """Test LockdownPolicyTimeseries indexing with an int."""
    policy_1 = lockdown_policy.LockdownPolicy(agriculture=0.3)
    policy_2 = lockdown_policy.LockdownPolicy(agriculture=0.5)
    timeseries = lockdown_policy.LockdownTimeSeries(
        policies=[
            lockdown_policy.LockdownPolicyApplication(
                policy=policy_1,
                start=datetime.date(2020, 1, 10),
                end=datetime.date(2020, 1, 20),
            ),
            lockdown_policy.LockdownPolicyApplication(
                policy=policy_2,
                start=datetime.date(2020, 1, 20),
                end=datetime.date(2020, 1, 30),
            ),
        ]
    )
    assert timeseries[0] == policy_1
    assert timeseries[9] == policy_1
    assert timeseries[10] == policy_2
    assert timeseries[19] == policy_2
    assert timeseries[-1] == policy_2
    assert timeseries[-10] == policy_2
    assert timeseries[-20] == policy_1


def test_lockdown_policy_timeseries_indexable_with_date():
    """Test LockdownPolicyTimeseries indexing with an int."""
    policy_1 = lockdown_policy.LockdownPolicy(agriculture=0.3)
    policy_2 = lockdown_policy.LockdownPolicy(agriculture=0.5)
    timeseries = lockdown_policy.LockdownTimeSeries(
        policies=[
            lockdown_policy.LockdownPolicyApplication(
                policy=policy_1,
                start=datetime.date(2020, 1, 10),
                end=datetime.date(2020, 1, 20),
            ),
            lockdown_policy.LockdownPolicyApplication(
                policy=policy_2,
                start=datetime.date(2020, 1, 20),
                end=datetime.date(2020, 1, 30),
            ),
        ]
    )
    assert timeseries[datetime.date(2020, 1, 15)] == policy_1
    assert timeseries[datetime.date(2020, 1, 19)] == policy_1
    assert timeseries[datetime.date(2020, 1, 20)] == policy_2
    assert timeseries[datetime.date(2020, 1, 25)] == policy_2
    assert timeseries[datetime.date(2020, 1, 29)] == policy_2


def test_lockdown_policy_raises_exception_when_out_of_range():
    """Test LockdownPolicyTimeseries fails when out of range correctly."""
    policy = lockdown_policy.LockdownPolicy(agriculture=0.3)
    timeseries = lockdown_policy.LockdownTimeSeries(
        policies=[
            lockdown_policy.LockdownPolicyApplication(
                policy=policy,
                start=datetime.date(2020, 1, 10),
                end=datetime.date(2020, 1, 20),
            )
        ]
    )
    with pytest.raises(IndexError):
        _ = timeseries[datetime.date(2020, 1, 5)]
    with pytest.raises(IndexError):
        _ = timeseries[datetime.date(2020, 1, 25)]
    with pytest.raises(IndexError):
        _ = timeseries[10]
    with pytest.raises(IndexError):
        _ = timeseries[-11]


def test_lockdown_policy_with_int_slice():
    """Test LockdownPolicyTimeseries slices correctly."""
    policy_1 = lockdown_policy.LockdownPolicy(agriculture=0.3)
    policy_2 = lockdown_policy.LockdownPolicy(agriculture=0.5)
    timeseries = lockdown_policy.LockdownTimeSeries(
        policies=[
            lockdown_policy.LockdownPolicyApplication(
                policy=policy_1,
                start=datetime.date(2020, 1, 10),
                end=datetime.date(2020, 1, 20),
            ),
            lockdown_policy.LockdownPolicyApplication(
                policy=policy_2,
                start=datetime.date(2020, 1, 20),
                end=datetime.date(2020, 1, 30),
            ),
        ]
    )

    sliced_1 = timeseries[2:7]
    assert isinstance(sliced_1, lockdown_policy.LockdownTimeSeries)
    assert sliced_1.policies == [
        lockdown_policy.LockdownPolicyApplication(
            policy=policy_1,
            start=datetime.date(2020, 1, 12),
            end=datetime.date(2020, 1, 17),
        )
    ]

    sliced_2 = timeseries[8:15]
    assert isinstance(sliced_2, lockdown_policy.LockdownTimeSeries)
    assert sliced_2.policies == [
        lockdown_policy.LockdownPolicyApplication(
            policy=policy_1,
            start=datetime.date(2020, 1, 18),
            end=datetime.date(2020, 1, 20),
        ),
        lockdown_policy.LockdownPolicyApplication(
            policy=policy_2,
            start=datetime.date(2020, 1, 20),
            end=datetime.date(2020, 1, 25),
        ),
    ]

def test_lockdown_policy_slicing_with_no_end():
    """Test LockdownPolicyTimeseries slices correctly with infinite policies."""
    policy = lockdown_policy.LockdownPolicy(agriculture=0.3)
    timeseries = lockdown_policy.LockdownTimeSeries(
        policies=[
            lockdown_policy.LockdownPolicyApplication(
                policy=policy,
                start=datetime.date(2020, 1, 10),
                end=None,
            )
        ]
    )
    sliced = timeseries[:100]
    assert isinstance(sliced, lockdown_policy.LockdownTimeSeries)
    assert sliced.policies == [
        lockdown_policy.LockdownPolicyApplication(
            policy=policy,
            start=datetime.date(2020, 1, 10),
            end=datetime.date(2020, 1, 10) + datetime.timedelta(days=100),
        ),
    ]


def test_lockdown_policy_slicing_to_end():
    """Test LockdownPolicyTimeseries slices correctly with infinite policies."""
    policy = lockdown_policy.LockdownPolicy(agriculture=0.3)
    timeseries = lockdown_policy.LockdownTimeSeries(
        policies=[
            lockdown_policy.LockdownPolicyApplication(
                policy=policy,
                start=datetime.date(2020, 1, 10),
                end=datetime.date(2020, 1, 20),
            )
        ]
    )
    sliced = timeseries[5:]
    assert isinstance(sliced, lockdown_policy.LockdownTimeSeries)
    assert sliced.policies == [
        lockdown_policy.LockdownPolicyApplication(
            policy=policy,
            start=datetime.date(2020, 1, 15),
            end=datetime.date(2020, 1, 20),
        ),
    ]
