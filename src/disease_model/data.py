"""Module for objects holding data for the models."""
import attr


@attr.s
class PopulationData:  # pylint: disable=too-few-public-methods
    """Struct for holding population data."""
    population_size: int = attr.ib()
    life_expectancy: float = attr.ib(default=72.0)


@attr.s
class HealthData:  # pylint: disable=too-few-public-methods
    """Struct for holding a time-series of health data."""
    confirmed_cases = attr.ib()
    recovered = attr.ib()
    deaths = attr.ib()

    def __len__(self):
        return len(self.confirmed_cases)

    def __getitem__(self, key):
        return HealthData(confirmed_cases=self.confirmed_cases[key],
                          recovered=self.recovered[key],
                          deaths=self.deaths[key])
