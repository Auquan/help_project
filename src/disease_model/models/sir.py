"""Simple SIR model."""
from typing import Tuple

import numpy as np
import pandas as pd
from scipy import integrate
from scipy import optimize
from help_project.src.disease_model import base_model
from help_project.src.disease_model import data
from help_project.src.disease_model import parameter
from help_project.src.exitstrategies import lockdown_policy


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
        self.parameter_mapper = {}

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
                health_data: data.HealthData):
        """Residue for a solution to the model.

        Args:
            params: The chosen params to try.
            population_data: Relevant data for the population of interest.
            health_data: Time-series of confirmed infections and deaths.

        Returns:
            Mean Square Error for the time series of the health data.
        """
        model = SIR(self.parameter_config)
        model.set_params(params)
        starting_health_data = health_data[[0]]
        expected_health_data = health_data[1:]
        predictions = model.predict_with_current_params(
            population_data, starting_health_data, len(health_data) - 1)
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

        Args:
            population_data: Relevant data for the population of interest.
            health_data: Time-series of confirmed infections and deaths.
            policy_data: Time-series of lockdown policy applied.

        Returns:
            Whether the optimization was successful in finding a solution.
        """
        for policy_application in policy_data.policies:
            health_data_subset = health_data[policy_application.start:policy_application.end]
            model = SIR(self.parameter_config)
            # pylint: disable=protected-access
            if model.fit_single_policy(population_data, health_data_subset):
                self.parameter_mapper[policy_application.policy] = model.get_params()

    def fit_single_policy(
            self,
            population_data: data.PopulationData,
            health_data: data.HealthData) -> bool:
        """Fit the model to the given data.

        Args:
            population_data: Relevant data for the population of interest.
            health_data: Time-series of confirmed infections and deaths.

        Returns:
            Whether the optimization was successful in finding a solution.
        """
        result = optimize.differential_evolution(
            self.residue,
            bounds=[param.bounds for param in self.parameter_config],
            args=(population_data,
                  health_data),
            workers=-1,
            updating='deferred',
        )

        if result.success:
            self.set_params(result.x)
        return result.success

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
        current_health_data = past_health_data
        predictions = []
        for policy_application in future_policy_data.policies:
            params = self.parameter_mapper[policy_application.policy]
            model = SIR(self.parameter_config)
            model.set_params(params)
            # pylint: disable=protected-access
            next_health_data = model.predict_with_current_params(
                population_data,
                current_health_data,
                forecast_length=len(policy_application),
            )
            predictions.append(next_health_data)
            current_health_data = next_health_data

        index = pd.date_range(
            future_policy_data.start, future_policy_data.end, closed='left')
        return data.HealthData(
            confirmed_cases=pd.Series(
                data=np.concatenate([p.confirmed_cases for p in predictions]),
                index=index,
            ),
            recovered=pd.Series(
                data=np.concatenate([p.recovered for p in predictions]),
                index=index,
            ),
            deaths=pd.Series(
                data=np.concatenate([p.deaths for p in predictions]),
                index=index,
            ),
        )

    def predict_with_current_params(
            self,
            population_data: data.PopulationData,
            past_health_data: data.HealthData,
            forecast_length: int) -> data.HealthData:
        """Get predictions.

        Args:
            population_data: Relevant data for the population of interest.
            past_health_data: Time-series of confirmed infections and deaths.
            forecast_length: Length of the forecast to produce.

        Returns:
            Predicted time-series of health data matching the length of the
            given policy.
        """
        missing_params = [param.name for param in self.parameter_config
                          if param.name not in self.params]
        if missing_params:
            raise RuntimeError(
                'Model params not set (%s). '
                'Fit the model or set them manually' % missing_params)

        initial_health_data = past_health_data[-1]
        initial_susceptible = (
            population_data.population_size -
            initial_health_data.confirmed_cases -
            initial_health_data.recovered -
            initial_health_data.deaths)

        prediction = integrate.solve_ivp(
            self.differential_equations,
            t_span=(0, forecast_length),
            t_eval=np.arange(1, forecast_length + 1),
            y0=(initial_susceptible,
                initial_health_data.confirmed_cases,
                initial_health_data.recovered,
                initial_health_data.deaths),
            args=self.parameter_config.flatten(self.params))

        (_,
         predicted_infected,
         predicted_recovered,
         predicted_deaths) = prediction.y

        return data.HealthData(
            confirmed_cases=predicted_infected,
            recovered=predicted_recovered,
            deaths=predicted_deaths)
