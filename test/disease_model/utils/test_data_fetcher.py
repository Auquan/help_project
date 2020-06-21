"""Tests for data_fetcher module."""
from help_project.src.disease_model.utils import data_fetcher


def test_initialize():
    """Test that the initializer works."""
    data_fetcher.DataFetcher()


def test_get_countries():
    """Test that it works and returns an appropriate number of results."""
    fetcher = data_fetcher.DataFetcher()
    assert 200 < len(fetcher.get_countries()) < 300


def test_get_population_data():
    """Test that it works and returns an appropriate number."""
    fetcher = data_fetcher.DataFetcher()
    cl_population_data = fetcher.get_population_data('Chile')
    assert 1e7 < cl_population_data.population_size < 2e7
