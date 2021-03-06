"""This is the external API, that other teams can call."""
from typing import Optional
from typing import Sequence

from help_project.src.disease_model import base_model
from help_project.src.disease_model import data
from help_project.src.disease_model.models import seir
from help_project.src.disease_model.models import sir
from help_project.src.exitstrategies import lockdown_policy


class EnsembleModel(base_model.BaseDiseaseModel):
    """Class for Ensemble model."""

    def __init__(
            self,
            models: Optional[Sequence[base_model.BaseDiseaseModel]] = None):
        if not models:
            models = [sir.SIR(), seir.SEIR()]
        self.models = list(models)

    def fit(self,
            population_data: data.PopulationData,
            health_data: data.HealthData,
            policy_data: lockdown_policy.LockdownTimeSeries) -> bool:
        """Fit the model to the given data.

        Args:
            population_data: Relevant data for the population of interest.
            health_data: Time-series of confirmed infections and deaths.
            policy_data: Time-series of lockdown policy applied.

        Returns:
            Whether the optimization was succesful for all models.
        """
        return all([model.fit(population_data, health_data, policy_data)
                    for model in self.models])

    def predict(self,
                population_data: data.PopulationData,
                past_health_data: data.HealthData,
                future_policy_data: lockdown_policy.LockdownTimeSeries) -> data.HealthData:
        """Get predictions.

        Args:
            population_data: Relevant data for the population of interest.
            past_health_data: Time-series of confirmed infections and deaths.
            future_policy_data: Time-series of lockdown policy to predict for.

        Returns:
            Averaged predictions of time-series of health data matching the
            length of the given policy.
        """
        predictions = [
            model.predict(
                population_data, past_health_data, future_policy_data)
            for model in self.models
        ]
        return data.HealthData.average(predictions)
