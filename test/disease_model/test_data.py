"""Test for the data module."""
import pytest
import numpy as np
import pandas as pd
from help_project.src.disease_model import data


def test_average_numpy():
    """Test that the average time series is calculated properly from an nparray."""
    data_1 = data.HealthData(
        confirmed_cases=np.array([0, 1, 2]),
        recovered=np.array([0, 0, 0]),
        deaths=np.array([0, 0, 1]),
    )
    data_2 = data.HealthData(
        confirmed_cases=np.array([1, 1, 1]),
        recovered=np.array([0, 0, 1]),
        deaths=np.array([0, 0, 2]),
    )
    avg = data.HealthData.average([data_1, data_2])
    np.testing.assert_array_equal(
        avg.confirmed_cases,
        [0.5, 1.0, 1.5])
    np.testing.assert_array_equal(
        avg.recovered,
        [0, 0, .5])
    np.testing.assert_array_equal(
        avg.deaths,
        [0, 0, 1.5])


def test_average_list():
    """Test that the average time series is calculated properly from a list."""
    data_1 = data.HealthData(
        confirmed_cases=[0, 1, 2],
        recovered=[0, 0, 0],
        deaths=[0, 0, 1],
    )
    data_2 = data.HealthData(
        confirmed_cases=[1, 1, 1],
        recovered=[0, 0, 1],
        deaths=[0, 0, 2],
    )
    avg = data.HealthData.average([data_1, data_2])
    np.testing.assert_array_equal(
        avg.confirmed_cases,
        [0.5, 1.0, 1.5])
    np.testing.assert_array_equal(
        avg.recovered,
        [0, 0, .5])
    np.testing.assert_array_equal(
        avg.deaths,
        [0, 0, 1.5])


def test_average_series():
    """Test that the average time series is calculated properly from a series."""
    data_1 = data.HealthData(
        confirmed_cases=pd.Series([0, 1, 2]),
        recovered=pd.Series([0, 0, 0]),
        deaths=pd.Series([0, 0, 1]),
    )
    data_2 = data.HealthData(
        confirmed_cases=pd.Series([1, 1, 1]),
        recovered=pd.Series([0, 0, 1]),
        deaths=pd.Series([0, 0, 2]),
    )
    avg = data.HealthData.average([data_1, data_2])
    np.testing.assert_array_equal(
        avg.confirmed_cases,
        [0.5, 1.0, 1.5])
    np.testing.assert_array_equal(
        avg.recovered,
        [0, 0, .5])
    np.testing.assert_array_equal(
        avg.deaths,
        [0, 0, 1.5])


def test_average_with_missing_values():
    """Test that the average time series is calculated ignoring missing values."""
    data_1 = data.HealthData(
        confirmed_cases=[0, 1, 2],
        recovered=[0, 0, 0],
        deaths=[0, 0, 1],
        exposed_cases=[0, 0, 1],
    )
    data_2 = data.HealthData(
        confirmed_cases=[1, 1, 1],
        recovered=[0, 0, 1],
        deaths=[0, 0, 2],
        unreported_cases=[0, 0, 5],
    )
    avg = data.HealthData.average([data_1, data_2])
    np.testing.assert_array_equal(
        avg.confirmed_cases,
        [0.5, 1.0, 1.5])
    np.testing.assert_array_equal(
        avg.recovered,
        [0, 0, .5])
    np.testing.assert_array_equal(
        avg.deaths,
        [0, 0, 1.5])
    np.testing.assert_array_equal(
        avg.exposed_cases,
        [0, 0, 1])
    np.testing.assert_array_equal(
        avg.unreported_cases,
        [0, 0, 5])


def test_concatenate_numpy():
    """Test that the average time series is calculated properly."""
    data_1 = data.HealthData(
        confirmed_cases=np.array([0, 1, 2]),
        recovered=np.array([0, 0, 0]),
        deaths=np.array([0, 0, 1]),
    )
    data_2 = data.HealthData(
        confirmed_cases=np.array([2, 1, 1]),
        recovered=np.array([0, 0, 1]),
        deaths=np.array([1, 2, 1]),
    )
    avg = data.HealthData.concatenate([data_1, data_2])
    np.testing.assert_array_equal(
        avg.confirmed_cases,
        [0, 1, 2, 2, 1, 1])
    np.testing.assert_array_equal(
        avg.recovered,
        [0, 0, 0, 0, 0, 1])
    np.testing.assert_array_equal(
        avg.deaths,
        [0, 0, 1, 1, 2, 1])


def test_concatenate_series():
    """Test that the average time series is calculated properly."""
    data_1 = data.HealthData(
        confirmed_cases=pd.Series([0, 1, 2]),
        recovered=pd.Series([0, 0, 0]),
        deaths=pd.Series([0, 0, 1]),
    )
    data_2 = data.HealthData(
        confirmed_cases=pd.Series([2, 1, 1]),
        recovered=pd.Series([0, 0, 1]),
        deaths=pd.Series([1, 2, 1]),
    )
    avg = data.HealthData.concatenate([data_1, data_2])
    np.testing.assert_array_equal(
        avg.confirmed_cases,
        [0, 1, 2, 2, 1, 1])
    np.testing.assert_array_equal(
        avg.recovered,
        [0, 0, 0, 0, 0, 1])
    np.testing.assert_array_equal(
        avg.deaths,
        [0, 0, 1, 1, 2, 1])


def test_concatenate_series_with_unmatched_data():
    """Test that the average time series is calculated properly."""
    data_1 = data.HealthData(
        confirmed_cases=pd.Series([0, 1, 2]),
        recovered=pd.Series([0, 0, 0]),
        deaths=pd.Series([0, 0, 1]),
        exposed_cases=pd.Series([0, 0, 0]),
    )
    data_2 = data.HealthData(
        confirmed_cases=pd.Series([2, 1, 1]),
        recovered=pd.Series([0, 0, 1]),
        deaths=pd.Series([1, 2, 1]),
    )

    with pytest.raises(ValueError):
        avg = data.HealthData.concatenate([data_1, data_2])
        print(avg.exposed_cases)


def test_set_index_on_series():
    """Test that the index is modified on all series."""
    data_sample = data.HealthData(
        confirmed_cases=pd.Series([0, 1, 2]),
        recovered=pd.Series([0, 0, 0]),
        deaths=pd.Series([0, 0, 1]),
        exposed_cases=pd.Series([0, 0, 0]),
        unreported_cases=None
    )
    index = ['a', 'b', 'c']
    data_sample.index = index
    np.testing.assert_array_equal(data_sample.confirmed_cases.index, index)
    np.testing.assert_array_equal(data_sample.recovered.index, index)
    np.testing.assert_array_equal(data_sample.deaths.index, index)
    np.testing.assert_array_equal(data_sample.exposed_cases.index, index)
    assert data_sample.unreported_cases is None


def test_set_index_on_nparray():
    """Test that the index is modified on all series."""
    data_sample = data.HealthData(
        confirmed_cases=np.array([0, 1, 2]),
        recovered=np.array([0, 0, 0]),
        deaths=np.array([0, 0, 1]),
        exposed_cases=np.array([0, 0, 0]),
        unreported_cases=None
    )
    index = ['a', 'b', 'c']
    data_sample.index = index
    np.testing.assert_array_equal(data_sample.confirmed_cases.index, index)
    np.testing.assert_array_equal(data_sample.recovered.index, index)
    np.testing.assert_array_equal(data_sample.deaths.index, index)
    np.testing.assert_array_equal(data_sample.exposed_cases.index, index)
    assert data_sample.unreported_cases is None
