"""Class for a mapper that maps the lockdown strategy for all the models."""

from os import path
import datetime as dt
import pickle
import pandas as pd
from sklearn.cluster import KMeans
from help_project.src.exitstrategies import interface
from help_project.src.disease_model.models import auquan_seir
from help_project.src.disease_model.utils import data_fetcher


class ParameterMapper:
    """Class for parameter mapper."""

    def __init__(self, to_model=None):
        self.to_model = to_model
        strategies = interface.ExitStrategies().get_exit_strategies()
        for key in strategies:
            # TODO
            # remove hardcoded base date
            dates = pd.date_range(
                start=dt.datetime(2020, 2, 29), periods=len(strategies[key]))
            strategies[key].index = dates
            strategies[key] = strategies[key].drop_duplicates()
        self.strategies = strategies
        self.parameters = {}
        self.clustering_model = None

    def fit(self, use_cached_mapper=False):
        """Fit the parameter mapper for a particular model."""
        # Disable pycharm warning
        # pylint: disable=too-many-locals
        dir_path = path.dirname(path.realpath(__file__))
        if use_cached_mapper and path.exists(
                dir_path + '/data/mapper.pickle'):
            file = open(dir_path + '/data/mapper.pickle', 'rb')
            self.clustering_model, self.parameters = pickle.load(file)
            file.close()
        else:
            params = []
            fetcher = data_fetcher.DataFetcher()
            all_policies = []
            for key in self.strategies:
                # TODO
                # Ideally country should change for each key, using india for
                # now
                country = 'India'
                population_data = fetcher.get_population_data(country)
                health_data = fetcher.get_health_data(country)
                all_policies.append(self.strategies[key])
                for i in range(len(self.strategies[key])):
                    date = self.strategies[key].index[i]
                    health_model = auquan_seir.AuquanSEIR(start_date=date)
                    health_model.fit(
                        population_data=population_data,
                        health_data=health_data,
                        policy_data=None)
                    params.append(health_model.params)
            df_all_policies = pd.concat(all_policies, axis=0)
            clustering_model = KMeans(n_clusters=len(df_all_policies))
            clustering_model.fit(df_all_policies)
            self.clustering_model = clustering_model
            clusters = clustering_model.predict(df_all_policies)
            for i, cluster in enumerate(clusters):
                self.parameters[cluster] = params[i]
            file = open(dir_path + '/data/mapper.pickle', 'wb')
            pickle.dump((clustering_model, self.parameters), file)
            file.close()

    def map(self, lockdown_policy):
        """Map the new lockdown vector."""
        cluster = self.clustering_model.predict([lockdown_policy])[0]
        return self.parameters[cluster]
