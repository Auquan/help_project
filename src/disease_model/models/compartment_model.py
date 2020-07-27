"""Simple SIR model."""
import copy
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

import numpy as np
import pandas as pd
from scipy import integrate
from scipy import optimize
from help_project.src.disease_model import base_model
from help_project.src.disease_model import data
from help_project.src.disease_model import parameter
from help_project.src.exitstrategies import lockdown_policy


class CompartmentModel(base_model.BaseDiseaseModel):
    """Base compartment model.

    In a compartment model, people are allocated to compartments and
    differential equations define the change of these over time.
    """

    def __init__(self, parameter_config: parameter.ParameterConfig):
        self.params = {}
        self.parameter_config = parameter_config
        self.parameter_mapper = {}

    def differential_equations(
            self, _,
            compartments: Tuple[float, ...],
            *args: Tuple[float, ...]):
        """Differential equations for this model.

        Args:
            _: Timestep, which is not used.
            compartments: Tuple of population in each compartment.
            *args: Parameters used for the equations as a Tuple.

        Returns:
            Derivatives for each compartment.
        """
        raise NotImplementedError()

    def compute_initial_state(
            self,
            population_data: data.PopulationData,
            past_health_data: data.HealthData,
            params: Dict) -> Sequence[float]:
        """Compute the initial state used by the model for its predictions.

        Args:
            population_data: Relevant data for the population of interest.
            past_health_data: Time-series of confirmed infections and deaths.
            params: The parameters to use.

        Returns:
            A list with the initial values for each compartment.
        """
        raise NotImplementedError()

    def format_output(
            self, compartments: Sequence[Sequence[float]]) -> data.HealthData:
        """Convert the compartments prediction to the HealthData output.

        Args:
            compartments: Sequence of time series for all compartments.

        Returns:
            HealthData instance with the predicted time series.
        """
        raise NotImplementedError()

    def residue(self,
                params: Tuple[float, ...],
                population_data: data.PopulationData,
                health_data: data.HealthData):
        """Residue for a solution to the model.

        Args:
            params: The chosen params to try.
            population_data: Relevant data for the population of interest.
            health_data: Time-series of confirmed infections and deaths.

        Returns:
            Mean Square Error for the time series of the health data.
        """
        starting_health_data = health_data[[0]]
        parsed_params = self.parameter_config.parse(params)
        predictions = self.predict_with_params(
            population_data,
            starting_health_data,
            forecast_length=len(health_data) - 1,
            params=parsed_params,
        )

        expected_health_data = health_data[1:]
        deltas = [
            predictions.confirmed_cases - expected_health_data.confirmed_cases,
            predictions.recovered - expected_health_data.recovered,
            predictions.deaths - expected_health_data.deaths,
        ]
        return sum([np.square(d).mean() for d in deltas])

    def fit(self,
            population_data: data.PopulationData,
            health_data: data.HealthData,
            policy_data: lockdown_policy.LockdownTimeSeries) -> bool:
        """Fit the model to the given data.

        Splits the policy time series into components with a stable policy.
        Then does the fit process separately for each of these slices and
        aggregates the resulting params.

        Args:
            population_data: Relevant data for the population of interest.
            health_data: Time-series of confirmed infections and deaths.
            policy_data: Time-series of lockdown policy applied.

        Returns:
            Whether the optimization was successful in finding a solution.
        """
        policies = []
        params = []
        for policy_application in policy_data.policies:
            health_data_subset = health_data[policy_application.start:policy_application.end]
            computed_params = self.compute_fit_for_single_policy(
                population_data, health_data_subset)
            if computed_params:
                policies.append(policy_application)
                params.append(computed_params)

        self.aggregate_and_save_params(policies, params)

    def compute_fit_for_single_policy(
            self,
            population_data: data.PopulationData,
            health_data: data.HealthData) -> Optional[Dict]:
        """Fit the model to the given data.

        Args:
            population_data: Relevant data for the population of interest.
            health_data: Time-series of confirmed infections and deaths.

        Returns:
            The computed params as a dict if the optimization was successful.
        """
        result = optimize.differential_evolution(
            self.residue,
            bounds=tuple(param.bounds for param in self.parameter_config),
            args=(population_data, health_data),
            workers=-1,
            updating='deferred',
        )

        return (self.parameter_config.parse(result.x)
                if result.success else None)

    def predict(self,
                population_data: data.PopulationData,
                past_health_data: data.HealthData,
                future_policy_data: lockdown_policy.LockdownTimeSeries,
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
        current_health_data = past_health_data
        predictions = []
        for policy_application in future_policy_data.policies:
            params = self.get_params()
            mapper_params = self.parameter_mapper.get(policy_application.policy)
            # Update params with the multiplicative factors from the mapper
            for param, value in mapper_params.items():
                params[param] *= value

            next_health_data = self.predict_with_params(
                population_data,
                current_health_data,
                forecast_length=len(policy_application),
                params=params,
            )
            predictions.append(next_health_data)
            current_health_data = next_health_data

        index = pd.date_range(
            future_policy_data.start, future_policy_data.end, closed='left')

        output = data.HealthData.concatenate(predictions)
        output.index = index
        return output

    def predict_with_params(
            self,
            population_data: data.PopulationData,
            past_health_data: data.HealthData,
            forecast_length: int,
            params: Dict) -> data.HealthData:
        """Get predictions.

        Args:
            population_data: Relevant data for the population of interest.
            past_health_data: Time-series of confirmed infections and deaths.
            forecast_length: Length of the forecast to produce.
            params: The parameters to use for the predictions.

        Returns:
            Predicted time-series of health data matching the length of the
            given policy.
        """
        missing_params = [param.name for param in self.parameter_config
                          if param.name not in params]
        if missing_params:
            raise RuntimeError(
                'Model params not set (%s). '
                'Fit the model or set them manually' % missing_params)

        initial_state = self.compute_initial_state(
            population_data, past_health_data, params)

        prediction = integrate.solve_ivp(
            fun=lambda t, y: self.differential_equations(t, y, tuple(self.parameter_config.flatten(params))),
            t_span=(0, forecast_length),
            t_eval=np.arange(1, forecast_length + 1),
            y0=initial_state)

        return self.format_output(prediction.y)

    def aggregate_params(self, computed_params, weights):
        """Aggregate the given parameters using the given weights.

        For policy independent parameters, the weighted average is computed.

        For policy dependent parameters, the maximum value is computed.
        This value can then be discounted sensibly by the parameter mapper.
        """
        agg_params = {}
        for params, weight in zip(computed_params, weights):
            for param in self.parameter_config:
                # For policy-dependent params, get the max to then discount it
                if param.policy_dependent:
                    agg_params[param.name] = max(
                        agg_params.get(param.name, 0),
                        params.get(param.name, 0),
                    )
                # For policy-independent params, get weighted average
                else:
                    agg_params[param.name] = (
                        agg_params.get(param.name, 0) +
                        params.get(param.name, 0) * weight)
        return agg_params

    def aggregate_and_save_params(
            self,
            policies: Sequence[lockdown_policy.LockdownPolicyApplication],
            computed_params: Sequence[Dict]):
        """Aggregate the params and save them to the model.

        - Policy-dependent parameters will be saved on the parameter mapper for
            each policy.
        - Policy-independent parameters will be averaged over all policies.

        Args:
            policies: The policy applications that are being used.
            computed_params: The params computed for each policy application.
        """
        total_timesteps = sum(len(p) for p in policies)
        general_params = self.aggregate_params(
            computed_params, [len(p) / total_timesteps for p in policies])
        parameter_mapper = {}
        for policy_application, params in zip(policies, computed_params):
            parameter_mapper[policy_application.policy] = {
                param.name: params[param.name] / general_params[param.name]
                for param in self.parameter_config
                if param.policy_dependent
            }
        self.set_params(general_params)
        self.parameter_mapper = parameter_mapper

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
