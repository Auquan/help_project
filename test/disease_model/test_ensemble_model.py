"""Test for ensemble model module."""
from unittest import mock
import numpy as np

from help_project.src.disease_model import base_model
from help_project.src.disease_model import data
from help_project.src.disease_model import ensemble_model
from help_project.src.disease_model.utils import data_fetcher
from help_project.src.exitstrategies import interface


def test_ensemble_model_fits_all_submodels():
    """Ensure ensemble model fits all the contained models."""
    submodel_1 = base_model.BaseDiseaseModel()
    submodel_2 = base_model.BaseDiseaseModel()
    submodel_1.fit = mock.MagicMock()
    submodel_2.fit = mock.MagicMock()
    ensemble = ensemble_model.EnsembleModel([submodel_1, submodel_2])
    ensemble.fit(None, None, None)

    submodel_1.fit.assert_called_once_with(None, None, None)
    submodel_2.fit.assert_called_once_with(None, None, None)


def test_ensemble_model_predict_averages_all_submodules():
    """Ensure ensemble model predicts using all the contained models."""
    submodel_1 = base_model.BaseDiseaseModel()
    submodel_2 = base_model.BaseDiseaseModel()
    result_1 = data.HealthData(
        confirmed_cases=np.array([1, 2]),
        recovered=np.array([0, 0]),
        deaths=np.array([0, 0]),
    )
    result_2 = data.HealthData(
        confirmed_cases=np.array([3, 0]),
        recovered=np.array([0, 1]),
        deaths=np.array([0, 2]),
    )
    expected = data.HealthData(
        confirmed_cases=np.array([2, 1]),
        recovered=np.array([0, 0.5]),
        deaths=np.array([0, 1]),
    )
    submodel_1.predict = mock.MagicMock(return_value=result_1)
    submodel_2.predict = mock.MagicMock(return_value=result_2)
    ensemble = ensemble_model.EnsembleModel([submodel_1, submodel_2])
    result = ensemble.predict(None, None, None)

    assert np.array_equal(result.confirmed_cases, expected.confirmed_cases)
    assert np.array_equal(result.recovered, expected.recovered)
    assert np.array_equal(result.deaths, expected.deaths)
    submodel_1.predict.assert_called_once_with(None, None, None)
    submodel_2.predict.assert_called_once_with(None, None, None)


def test_ensemble_model_runs_without_failure():
    """Ensure ensemble model runs end-to-end without failure."""
    fetcher = data_fetcher.DataFetcher()
    country = 'India'
    population_data = fetcher.get_population_data(country)
    health_data = fetcher.get_health_data(country)
    lockdown_vector = list(
        interface.ExitStrategies().get_exit_strategies().values())[0].values
    policy_data = data.PolicyData(lockdown=[0.2] * lockdown_vector.shape[1])
    model = ensemble_model.EnsembleModel()
    model.fit(population_data, health_data, None)
    health_output = model.predict(population_data, health_data, policy_data)
    assert health_output is not None
    assert len(health_output.confirmed_cases) > 0
    assert len(health_output.recovered) > 0
    assert len(health_output.deaths) > 0
