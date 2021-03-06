"""Simple SIR model."""
from typing import Sequence
from typing import Tuple

from help_project.src.disease_model import data
from help_project.src.disease_model import parameter
from help_project.src.disease_model.models import compartment_model


class SIR(compartment_model.CompartmentModel):
    """Simple compartment model.

    Compartments:
    - S: Susceptible
    - I: Infectious
    - R: Recovered
    - D: Dead

    Assumptions:
    - People become infectious as soon as they come in contact with the disease
    - The population mixes homegeneously
    - Survivors of the disease become permanently immune
    """

    DEFAULT_PARAMETER_CONFIG = parameter.ParameterConfig(
        # Policy Dependent
        parameter.Parameter(name='beta',
                            description='Infection rate',
                            bounds=(0, 10),
                            policy_dependent=True),
        # Policy Independent
        parameter.Parameter(name='gamma',
                            description='Recovery rate',
                            bounds=(1 / 30, 1 / 5)),
        parameter.Parameter(name='b',
                            description='Birth rate',
                            bounds=(0, 1 / 2)),
        parameter.Parameter(name='mu',
                            description='Base mortality rate',
                            bounds=(1 / 365 / 90, 1 / 365 / 30)),
        parameter.Parameter(name='mu_i',
                            description='Infected mortality rate',
                            bounds=(1 / 30, 1 / 5)),
        parameter.Parameter(name='cfr',
                            description='Case fatality rate',
                            bounds=(0, 0.05))
    )

    def __init__(self, parameter_config=None):
        """Initialize the SIR model."""
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

    def compute_initial_state(
            self,
            population_data: data.PopulationData,
            past_health_data: data.HealthData,
            _) -> Sequence[float]:
        """Compute the initial state used by the model for its predictions.

        Args:
            population_data: Relevant data for the population of interest.
            past_health_data: Time-series of confirmed infections and deaths.
            _: This model does not rely on the params to get the initial state.

        Returns:
            A list with the initial values for each compartment.
        """
        initial_health_data = past_health_data[-1]
        initial_susceptible = (
            population_data.population_size -
            initial_health_data.confirmed_cases -
            initial_health_data.recovered -
            initial_health_data.deaths)
        return (initial_susceptible,
                initial_health_data.confirmed_cases,
                initial_health_data.recovered,
                initial_health_data.deaths)

    def format_output(
            self, compartments: Sequence[Sequence[float]]) -> data.HealthData:
        """Convert the compartments prediction to the HealthData output.

        Args:
            compartments: Sequence of time series for all compartments.

        Returns:
            HealthData instance with the predicted time series.
        """
        (_,
         predicted_infected,
         predicted_recovered,
         predicted_deaths) = compartments

        return data.HealthData(
            confirmed_cases=predicted_infected,
            recovered=predicted_recovered,
            deaths=predicted_deaths)
