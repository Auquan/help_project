"""Simple SIR model."""
from typing import Dict
from typing import Sequence
from typing import Tuple

from help_project.src.disease_model import data
from help_project.src.disease_model import parameter
from help_project.src.disease_model.models import compartment_model
from help_project.src.exitstrategies import lockdown_policy


class SEIR(compartment_model.CompartmentModel):
    """Slightly more complex compartment model.

    Compartments:
    - S: Susceptible
    - E: Exposed
    - I: Infectious
    - R: Recovered
    - D: Dead

    Assumptions:
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
        parameter.Parameter(name='sigma',
                            description='Incubation rate',
                            bounds=(1 / 14, 1 / 2)),
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
                            bounds=(0, 0.05)),
        parameter.Parameter(name='initial_exposed_fr',
                            description='Initial fraction of the population that has been exposed',
                            bounds=(0, 1)),
    )

    def __init__(self, parameter_config=None):
        super().__init__(parameter_config or SEIR.DEFAULT_PARAMETER_CONFIG)
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
        s, e, i, r, _ = compartments
        population = s + e + i + r
        parameters = self.parameter_config.parse(args[0])
        beta = parameters['beta']
        gamma = parameters['gamma']
        sigma = parameters['sigma']
        b = parameters['b']
        mu = parameters['mu']
        mu_i = parameters['mu_i']
        cfr = parameters['cfr']

        ds = -(beta * s * i / population) + (b - mu) * s
        de = beta * s * i / population - sigma * e - mu * e
        di = sigma * e - (gamma * (1 - cfr) + mu_i * cfr) * i - mu * i
        dr = gamma * (1 - cfr) * i - mu * r
        dd = mu_i * cfr * i
        return ds, de, di, dr, dd

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
        initial_health_data = past_health_data[-1]
        initial_susceptible = (
            population_data.population_size -
            initial_health_data.confirmed_cases -
            initial_health_data.recovered -
            initial_health_data.deaths)
        initial_exposed = (
            initial_health_data.exposed_cases
            if initial_health_data.exposed_cases is not None
            else initial_susceptible * params['initial_exposed_fr'])
        return (initial_susceptible - initial_exposed,
                initial_exposed,
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
         predicted_exposed,
         predicted_infected,
         predicted_recovered,
         predicted_deaths) = compartments

        return data.HealthData(
            exposed_cases=predicted_exposed,
            confirmed_cases=predicted_infected,
            recovered=predicted_recovered,
            deaths=predicted_deaths,
        )

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
        super().aggregate_and_save_params(policies, computed_params)
        # Keep the last exposed fraction to be used for the initial data when predicting
        self.params['initial_exposed_fr'] = computed_params[-1]['initial_exposed_fr']
