"""Module for loss functions."""
from typing import Dict
from typing import NewType
from typing import Tuple
from typing import Union
import attr

from help_project.src.disease_model import data
from help_project.src.exitstrategies import lockdown_policy


LossValue = NewType('LossType', Union[float, Tuple[float, ...]])


@attr.s(frozen=True)
class Result:  # pylint: disable=too-few-public-methods
    """Struct for holding a solution and a loss value."""
    solution: lockdown_policy.LockdownTimeSeries = attr.ib()
    loss: LossValue = attr.ib()


class LossFunction:
    """A function to evaluate the 'badness' of a given outcome."""

    def compute(self,
                population_data: data.PopulationData,
                health_output: data.HealthData,
                economic_output: Dict) -> LossValue:
        """Compute the loss for a given health and economic output."""
        raise NotImplementedError()

    def __call__(self, *args, **kwargs) -> LossValue:
        """Shortcut to call the compute function."""
        return self.compute(*args, **kwargs)


class ParetoLoss(LossFunction):
    """Loss function which does not trade health and economic values."""

    def compute(self,
                population_data: data.PopulationData,
                health_output: data.HealthData,
                economic_output: Dict) -> LossValue:
        """Compute the loss as a tuple of health and economic losses."""
        return (self.health_loss(population_data, health_output),
                self.economic_loss(population_data, economic_output))

    @classmethod
    def health_loss(cls,
                    _: data.PopulationData,
                    health_output: data.HealthData) -> float:
        """Compute the health loss."""
        return sum(health_output.deaths)

    @classmethod
    def economic_loss(cls,
                      _: data.PopulationData,
                      economic_output: Dict) -> float:
        """Compute the economic loss."""
        return -sum(economic_output.values())


class WellbeingYears(LossFunction):  # pylint: disable=too-few-public-methods
    """Loss function which assigns a wellbeing value to all dimensions."""

    def __init__(self,
                 life_satisfaction: float = 7.5,
                 years_left_to_live: float = 12,
                 qaly_cost: float = 125000,
                 ):
        """Initialize the wellbeing years lost function."""
        self.life_satisfaction = life_satisfaction
        self.years_left_to_live = years_left_to_live
        self.qaly_cost = qaly_cost

    def compute(self,
                population_data: data.PopulationData,
                health_output: data.HealthData,
                economic_output: Dict) -> LossValue:
        """Compute the loss."""
        # Assume mean age
        mean_age = population_data.life_expectancy / 2
        mean_years_to_live = population_data.life_expectancy - mean_age
        health_wellbys = (
            population_data.population_size *
            mean_years_to_live *
            self.life_satisfaction)
        death_cost = (
            sum(health_output.deaths) *
            self.years_left_to_live *
            self.life_satisfaction)
        economic_wellbys = sum(economic_output.values()) / self.qaly_cost
        return -(health_wellbys - death_cost + economic_wellbys)


class ParetoFrontier():
    """Class to store the pareto frontier for a problem."""

    def __init__(self):
        self.frontier = []

    def update(self, result: Result):
        """Update the pareto frontier given a new point and loss value.

        The frontier will remain unchanged if any point dominates the new given
        point. If the new point in turn, dominates any points previously in the
        frontier, these points will be removed."""
        for pareto_result in self.frontier:
            if pareto_result.solution == result.solution:
                return  # No update - new point already exists.
            if ParetoFrontier.dominate(pareto_result.loss, result.loss):
                return  # No update - new loss is worse than some point

        # Update - keep only points that are not dominated by the new point
        self.frontier = [pareto_result
                         for pareto_result in self.frontier
                         if not ParetoFrontier.dominate(
                             result.loss, pareto_result.loss)]
        self.frontier.append(result)

    @classmethod
    def dominate(cls, loss_a: LossValue, loss_b: LossValue) -> bool:
        """Compute whether loss_a dominates loss_b."""
        try:
            return float(loss_a) < float(loss_b)
        except TypeError:
            assert len(loss_a) == len(loss_b), "Losses have different length"
            zipped_values = list(zip(loss_a, loss_b))

            return (any(a < b for a, b in zipped_values) and
                    all(a <= b for a, b in zipped_values))
