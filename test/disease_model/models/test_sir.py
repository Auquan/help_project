"""Test the sir module."""
import numpy as np
import pandas as pd

from help_project.src.disease_model import data
from help_project.src.disease_model.models import sir


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
    expected_prediction_size = 10
    future_policy = data.PolicyData(lockdown=[0] * expected_prediction_size)
    predictions = sir_model.predict(
        population_data, health_data, future_policy)

    # Dimensions must match the given policy
    assert len(predictions.confirmed_cases) == expected_prediction_size
    assert len(predictions.recovered) == expected_prediction_size
    assert len(predictions.deaths) == expected_prediction_size

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
    expected_prediction_size = 2
    future_policy = data.PolicyData(lockdown=[0] * expected_prediction_size)
    predictions = sir_model.predict(
        population_data, health_data, future_policy)

    # Dimensions must match the given policy
    assert len(predictions.confirmed_cases) == expected_prediction_size
    assert len(predictions.recovered) == expected_prediction_size
    assert len(predictions.deaths) == expected_prediction_size

    # Values should make sense
    assert predictions.confirmed_cases[1] > predictions.confirmed_cases[0]
    assert predictions.recovered[1] > predictions.recovered[0]
    assert all(predictions.deaths == 0)


def test_predictions_match_policy_index():
    """Test that the outputs have the correct format."""
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

    vector_policy = data.PolicyData(lockdown=[0, 0, 0])
    vector_predictions = sir_model.predict(
        population_data, health_data, vector_policy)
    isinstance(vector_predictions, np.ndarray)

    series_policy = data.PolicyData(
        lockdown=pd.Series(index=['a', 'b', 'c'], data=[0, 0, 0]))
    series_predictions = sir_model.predict(
        population_data, health_data, series_policy)
    print(series_predictions.deaths)
    np.testing.assert_array_equal(
        series_predictions.deaths.index, ['a', 'b', 'c'])


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

    initial_health_data = data.HealthData(
        confirmed_cases=[100],
        recovered=[0],
        deaths=[0],
    )
    expected_prediction_size = 100
    policy = data.PolicyData(lockdown=[0] * expected_prediction_size)
    ground_truth_predictions = ground_truth_model.predict(
        population_data, initial_health_data, policy)

    sir_model = sir.SIR()
    sir_model.fit(population_data,
                  ground_truth_predictions,
                  policy)

    # Verify that these are approximately the same
    np.testing.assert_array_almost_equal(
        sir_model.parameter_config.flatten(sir_model.params),
        sir_model.parameter_config.flatten(ground_truth_params),
        decimal=1)
