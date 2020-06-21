"""Module for getting country data."""
from os import path
import git
import pandas as pd

from help_project.src.disease_model import data


def clean_df(health_df):
    """Cleans the dataframe."""
    health_df = health_df.sum(axis=0)
    health_df = health_df[[d for d in health_df.index if d.find('/') > 0]].T
    health_df.index = pd.to_datetime(health_df.index)
    return health_df


def get_dfs():
    """Read the time series of deaths and infections from JHU data."""
    dir_path = path.dirname(path.realpath(__file__))
    data_dir = dir_path + '/../data/COVID-19/csse_covid_19_data/csse_covid_19_time_series/'
    rename = {'Country/Region': 'zone',
              'Province/State': 'sub_zone'}
    df_recovery = pd.read_csv(
        data_dir +
        'time_series_covid19_recovered_global.csv').rename(columns=rename)
    df_death = pd.read_csv(
        data_dir +
        'time_series_covid19_deaths_global.csv').rename(columns=rename)
    df_confirmed = pd.read_csv(
        data_dir +
        'time_series_covid19_confirmed_global.csv').rename(columns=rename)
    return df_recovery, df_death, df_confirmed


def get_population():
    """Read the population from the population csv."""
    dir_path = path.dirname(path.realpath(__file__))
    population = pd.read_csv(
        dir_path + '/../data/population-figures-by-country-csv_csv.csv')
    population = population.set_index('Country')
    return population


class DataFetcher():
    """Class for fetching data."""

    def __init__(self):
        dir_path = path.dirname(path.realpath(__file__))
        if not path.exists(dir_path + '/../data/COVID-19'):
            git.Git(
                dir_path + '/../data/').clone('https://github.com/CSSEGISandData/COVID-19.git')
        self.recovered_cases, self.deaths, self.confirmed_cases = get_dfs()
        self.population = get_population().Year_2016.to_dict()

    def get_countries(self):
        """Get the available country names."""
        return list(self.population.keys())

    def get_population_data(self, country: str):
        """Get the population data for a given country."""
        return data.PopulationData(population_size=self.population[country],
                                   demographics=None)

    def get_health_data(self, country: str):
        """Get the historical health data for a given country."""
        confirmed_cases = clean_df(self.confirmed_cases[(
            self.confirmed_cases['zone'] == country)])
        recovered = clean_df(self.recovered_cases[(
            self.recovered_cases['zone'] == country)])
        deaths = clean_df(self.deaths[(
            self.deaths['zone'] == country)])
        return data.HealthData(confirmed_cases=confirmed_cases,
                               recovered=recovered,
                               deaths=deaths)
