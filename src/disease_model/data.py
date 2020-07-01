"""Module for objects holding data for the models."""
from typing import Sequence
import attr
import numpy as np
import pandas as pd


@attr.s
class PopulationData:  # pylint: disable=too-few-public-methods
    """Struct for holding population data."""
    population_size = attr.ib()
    demographics = attr.ib()


@attr.s
class HealthData:  # pylint: disable=too-few-public-methods
    """Struct for holding a time-series of health data."""
    confirmed_cases = attr.ib()
    recovered = attr.ib()
    deaths = attr.ib()

    # Optional attributes
    exposed_cases = attr.ib(default=None)
    unreported_cases = attr.ib(default=None)

    @property
    def index(self):
        """Get the index used in the timeseries."""
        return self.confirmed_cases.index

    @index.setter
    def index(self, index):
        """Set the index used in the timeseries."""
        self.confirmed_cases = pd.Series(data=self.confirmed_cases, index=index)
        self.recovered = pd.Series(data=self.recovered, index=index)
        self.deaths = pd.Series(data=self.deaths, index=index)
        if self.exposed_cases is not None:
            self.exposed_cases = pd.Series(
                data=self.exposed_cases, index=index)
        if self.unreported_cases is not None:
            self.unreported_cases = pd.Series(
                data=self.unreported_cases, index=index)

    def __len__(self):
        return len(self.confirmed_cases)

    def __getitem__(self, key):
        return HealthData(
            # Required
            confirmed_cases=self.confirmed_cases[key],
            recovered=self.recovered[key],
            deaths=self.deaths[key],
            # Optional
            exposed_cases=(self.exposed_cases[key]
                           if self.exposed_cases is not None else None),
            unreported_cases=(self.unreported_cases[key]
                              if self.unreported_cases is not None else None))

    @classmethod
    def concatenate(cls, health_timeseries: Sequence):
        """Concatenate the given timeseries."""
        def concat_component(
                health_timeseries: Sequence, component: str):
            values = [getattr(t, component) for t in health_timeseries]
            if any(v is not None for v in values):
                if any(v is None for v in values):
                    raise ValueError(
                        'Timeseries have non-matching values (%s)' % component)
                try:
                    return pd.concat(values)
                except TypeError:
                    return np.concatenate(values)
            return None

        return HealthData(
            confirmed_cases=concat_component(health_timeseries, 'confirmed_cases'),
            recovered=concat_component(health_timeseries, 'recovered'),
            deaths=concat_component(health_timeseries, 'deaths'),
            unreported_cases=concat_component(health_timeseries, 'unreported_cases'),
            exposed_cases=concat_component(health_timeseries, 'exposed_cases'),
        )

    @classmethod
    def average(cls, health_timeseries: Sequence):
        """Average the given timeseries."""
        def average_component(
                health_timeseries: Sequence, component: str):
            values = [getattr(t, component) for t in health_timeseries]
            available_values = [v for v in values if v is not None]
            if not available_values:
                return None
            try:
                return sum(available_values) / len(available_values)
            except TypeError:  # If values are simple lists of ints, cast to nparray
                return sum(np.array(v) for v in available_values) / len(available_values)
        return HealthData(
            confirmed_cases=average_component(health_timeseries, 'confirmed_cases'),
            recovered=average_component(health_timeseries, 'recovered'),
            deaths=average_component(health_timeseries, 'deaths'),
            unreported_cases=average_component(health_timeseries, 'unreported_cases'),
            exposed_cases=average_component(health_timeseries, 'exposed_cases'),
        )
