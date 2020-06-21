"""Simple SIR model."""
from typing import Tuple

import numpy as np
import pandas as pd
from scipy import integrate
from scipy import optimize
from help_project.src.disease_model import base_model
from help_project.src.disease_model import data
from help_project.src.disease_model import parameter


class SIR(base_model.BaseDiseaseModel):
    """Simple compartment model.

    Compartments:
    - S: Susceptible
    - I: Infectious
    - R: Recovered
    - D: Dead

    It assumes that recovered people cannot contract the disease again.
    """

    DEFAULT_PARAMETER_CONFIG = parameter.ParameterConfig(
        parameter.Parameter(name='beta',
                            description='Infection rate',
                            bounds=[0, 10]),
        parameter.Parameter(name='gamma',
                            description='Recovery rate',
                            bounds=[1 / 30, 1 / 5]),
        parameter.Parameter(name='b',
                            description='Birth rate',
                            bounds=[0, 1 / 2]),
        parameter.Parameter(name='mu',
                            description='Base mortality rate',
                            bounds=[1 / 365 / 30, 1 / 365 / 90]),
        parameter.Parameter(name='mu_i',
                            description='Infected mortality rate',
                            bounds=[1 / 30, 1 / 5]),
        parameter.Parameter(name='cfr',
                            description='Case fatality rate',
                            bounds=[0, 0.05])
    )

    def __init__(self, parameter_config=None):
        super().__init__(parameter_config or SIR.DEFAULT_PARAMETER_CONFIG)

    def differential_equations(
            self, _,
            compartments: Tuple[float, float, float],
            *args: Tuple[float, ...]):
        """Differential equations for this model.

        Args:
            _: Timestep, which is not used.
            compartments: Tuple of population in each compartment (S, I, R).
            *args: Parameters used for the equations as a Tuple.

        Returns:
            Derivatives for each compartment.
        """
        # pylint: disable=invalid-name,too-many-locals
        s, i, r, _ = compartments
        population = s + i + r
        parameters = self.parameter_config.parse(args)
        beta = parameters['beta']
        gamma = parameters['gamma']
        b = parameters['b']
        mu = parameters['mu']
        mu_i = parameters['mu_i']
        cfr = parameters['cfr']

        ds = (-beta * i / population + b - mu) * s
        di = (beta * s / population - gamma * (1 - cfr) - mu_i * cfr - mu) * i
        dr = gamma * (1 - cfr) * i - mu * r
        dd = mu_i * cfr * i
        return ds, di, dr, dd

    def residue(self,
                params: Tuple[float, ...],
                population_data: data.PopulationData,
                health_data: data.HealthData,
                policy_data: data.PolicyData):
        """Residue for a solution to the model.

        Args:
            params: The chosen params to try.
            population_data: Relevant data for the population of interest.
            health_data: Time-series of confirmed infections and deaths.
            policy_data: Time-series of lockdown policy applied.

        Returns:
            Mean Square Error for the time series of the health data.
        """
        model = SIR(self.parameter_config)
        model.set_params(params)
        starting_health_data = health_data[[0]]
        expected_health_data = health_data[1:]
        predictions = model.predict(
            population_data, starting_health_data, policy_data[1:])
        deltas = [
            predictions.confirmed_cases - expected_health_data.confirmed_cases,
            predictions.recovered - expected_health_data.recovered,
            predictions.deaths - expected_health_data.deaths,
        ]
        return sum([np.square(d).mean() for d in deltas])

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
        result = optimize.differential_evolution(
            self.residue,
            bounds=[param.bounds for param in self.parameter_config],
            args=(population_data,
                  health_data,
                  policy_data),
            workers=-1,
            updating='deferred',
        )

        if result.success:
            self.set_params(result.x)
        return result.success

    def predict(self,
                population_data: data.PopulationData,
                past_health_data: data.HealthData,
                future_policy_data: data.PolicyData,
                use_cached_mapper: bool = True) -> data.HealthData:
        """Get predictions.

        Args:
            population_data: Relevant data for the population of interest.
            past_health_data: Time-series of confirmed infections and deaths.
            future_policy_data: Time-series of lockdown policy to predict for.

        Returns:
            Predicted time-series of health data matching the length of the
            given policy.
        """
        # Disable pycharm warning
        # pylint: disable=too-many-locals
        missing_params = [param.name for param in self.parameter_config
                          if param.name not in self.params]
        if missing_params:
            raise RuntimeError(
                'Model params not set (%s). '
                'Fit the model or set them manually' % missing_params)

        initial_confirmed_cases = past_health_data.confirmed_cases[-1]
        initial_recovered = past_health_data.recovered[-1]
        initial_deaths = past_health_data.deaths[-1]

        initial_susceptible = (
            population_data.population_size -
            (initial_confirmed_cases + initial_recovered + initial_deaths))

        forecast_length = len(future_policy_data.lockdown)
        prediction = integrate.solve_ivp(
            self.differential_equations,
            t_span=(0, forecast_length),
            t_eval=np.arange(forecast_length),
            y0=(initial_susceptible,
                initial_confirmed_cases,
                initial_recovered,
                initial_deaths),
            args=self.parameter_config.flatten(self.params))

        (_,
         predicted_infected,
         predicted_recovered,
         predicted_deaths) = prediction.y

        if isinstance(future_policy_data.lockdown, pd.Series):
            index = future_policy_data.lockdown.index
            predicted_infected = pd.Series(
                index=index,
                data=predicted_infected)
            predicted_recovered = pd.Series(
                index=index,
                data=predicted_recovered)
            predicted_deaths = pd.Series(
                index=index,
                data=predicted_deaths)
        return data.HealthData(
            confirmed_cases=predicted_infected,
            recovered=predicted_recovered,
            deaths=predicted_deaths)
