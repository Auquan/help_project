"""Base class for all models."""
import copy
from typing import Dict
from typing import Sequence
from typing import Union

from help_project.src.disease_model import data


class BaseDiseaseModel:
    """Base Disease Model for other models to inherit from."""

    def __init__(self, parameter_config=None):
        """Initialize the model."""
        self.params = {}
        self.parameter_config = parameter_config

    def fit(self,
            population_data: data.PopulationData,
            health_data: data.HealthData,
            policy_data: data.PolicyData) -> bool:
        """Fit the model to the given data.

        Args:
            population_data: Relevant data for the population of interest.
            health_data: Time-series of confirmed infections and deaths.
            policy_data: Time-series of lockdown policy applied.

        Returns:
            Whether the optimization was successful in finding a solution.
        """
        raise NotImplementedError()

    def set_params(self, values: Union[Dict, Sequence]):
        """Setter for param values.

        Can take either a list of parameters or a dictionary.
        """
        if not self.parameter_config:
            raise ValueError('No parameter config set.')
        if not isinstance(values, dict):
            values = self.parameter_config.parse(values)
        self.params = copy.deepcopy(values)

    def get_params(self) -> Dict:
        """Getter for params."""
        return copy.deepcopy(self.params)

    def predict(self,
                population_data: data.PopulationData,
                past_health_data: data.HealthData,
                future_policy_data: data.PolicyData,
                use_cached_mapper: bool) -> data.HealthData:
        """Get predictions.

        Args:
            population_data: Relevant data for the population of interest.
            past_health_data: Time-series of confirmed infections and deaths.
            future_policy_data: Time-series of lockdown policy to predict for.

        Returns:
            Predicted time-series of health data matching the length of the
            given policy.
        """
        raise NotImplementedError()
