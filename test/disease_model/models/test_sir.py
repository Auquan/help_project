"""Test the sir module."""
import datetime
import pytest
import numpy as np
import pandas as pd

from help_project.src.disease_model import data
from help_project.src.disease_model.models import sir
from help_project.src.exitstrategies import lockdown_policy


def test_predict_with_no_cases():
    """Test that the predict function makes sense."""
    population_data = data.PopulationData(
        population_size=1e6,
        demographics=None,
    )
    sir_model = sir.SIR()
    sir_model.set_params({
        'beta': 2,
        'gamma': 0.1,
        'b': 0,
        'mu': 0,
        'mu_i': 0,
        'cfr': 0,
    })

    health_data = data.HealthData(
        confirmed_cases=[0],
        recovered=[0],
        deaths=[0],
    )
    forecast_length = 10
    predictions = sir_model.predict_with_current_params(
        population_data, health_data, forecast_length)

    # Dimensions must match the given policy
    assert len(predictions.confirmed_cases) == forecast_length
    assert len(predictions.recovered) == forecast_length
    assert len(predictions.deaths) == forecast_length

    # Values should all be zero since there were no cases to begin with
    assert all(predictions.confirmed_cases == 0)
    assert all(predictions.recovered == 0)
    assert all(predictions.deaths == 0)


def test_predict_with_some_cases():
    """Test that the predict function makes sense."""
    population_data = data.PopulationData(
        population_size=1e6,
        demographics=None,
    )
    sir_model = sir.SIR()
    sir_model.set_params({
        'beta': 2,
        'gamma': 0.1,
        'b': 0,
        'mu': 0,
        'mu_i': 0,
        'cfr': 0,
    })

    health_data = data.HealthData(
        confirmed_cases=[100],
        recovered=[0],
        deaths=[0],
    )
    forecast_length = 2
    predictions = sir_model.predict_with_current_params(
        population_data, health_data, forecast_length)

    # Dimensions must match the given policy
    assert len(predictions.confirmed_cases) == forecast_length
    assert len(predictions.recovered) == forecast_length
    assert len(predictions.deaths) == forecast_length

    # Values should make sense
    assert predictions.confirmed_cases[1] > predictions.confirmed_cases[0]
    assert predictions.recovered[1] > predictions.recovered[0]
    assert all(predictions.deaths == 0)


@pytest.mark.slow
def test_fit():
    """Test that the fit function obtains sensible params."""
    population_data = data.PopulationData(
        population_size=1e6,
        demographics=None,
    )

    ground_truth_params = {
        'beta': 0.5,
        'gamma': 0.1,
        'b': 0,
        'mu': 0,
        'mu_i': 0.1,
        'cfr': 0.1,
    }
    ground_truth_model = sir.SIR()
    ground_truth_model.set_params(ground_truth_params)

    initial_health_index = pd.DatetimeIndex([datetime.date(2020, 3, 1)])
    initial_health_data = data.HealthData(
        confirmed_cases=pd.Series(data=[100], index=initial_health_index),
        recovered=pd.Series(data=[0], index=initial_health_index),
        deaths=pd.Series(data=[0], index=initial_health_index),
    )
    forecast_length = 100
    policy = lockdown_policy.LockdownPolicy()
    policy_timeseries = lockdown_policy.LockdownTimeSeries(
        policies=[
            lockdown_policy.LockdownPolicyApplication(
                policy=policy,
                start=datetime.date(2020, 3, 2),
                end=datetime.date(2020, 3, 2) + datetime.timedelta(forecast_length),
            ),
        ]
    )
    ground_truth_model.parameter_mapper[policy] = ground_truth_params
    ground_truth_predictions = ground_truth_model.predict(
        population_data, initial_health_data, policy_timeseries)

    sir_model = sir.SIR()
    sir_model.fit(population_data,
                  ground_truth_predictions,
                  policy_timeseries)

    # Verify that these are approximately the same
    np.testing.assert_array_almost_equal(
        sir_model.parameter_config.flatten(sir_model.parameter_mapper[policy]),
        sir_model.parameter_config.flatten(ground_truth_params),
        decimal=1)
