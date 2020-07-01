"""Base class for all models."""
from help_project.src.disease_model import data
from help_project.src.exitstrategies import lockdown_policy


class BaseDiseaseModel:
    """Base Disease Model for other models to inherit from."""

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
            Whether the optimization was successful in finding a solution.
        """
        raise NotImplementedError()

    def predict(self,
                population_data: data.PopulationData,
                past_health_data: data.HealthData,
                future_policy_data: lockdown_policy.LockdownTimeSeries
                ) -> data.HealthData:
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
