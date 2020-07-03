"""Module for handling the optimization loop."""
import itertools
import random
from typing import Iterator
from typing import List
from typing import Optional

from help_project.src.disease_model import data
from help_project.src.disease_model import base_model as health
from help_project.src.economic_model.models import basic_lockdown_model as econ
from help_project.src.optimization import loss_function
from help_project.src.optimization import lockdown_config
from help_project.src.exitstrategies import lockdown_policy


class Optimizer:
    """Main optimization class."""

    def __init__(self,
                 config: lockdown_config.LockdownConfig,
                 loss: loss_function.LossFunction):
        """Initialize the optimizer."""
        self.config = config
        self.loss = loss
        self.results = []

    def optimize(self,
                 population_data: data.PopulationData,
                 health_model: health.BaseDiseaseModel,
                 economic_model: econ.EconomicLockdownModel,
                 n_steps: Optional[int] = None) -> List[loss_function.Result]:
        """Run the optimization loop."""
        pareto_frontier = loss_function.ParetoFrontier()

        step = 0
        while True:
            try:
                policy = self.propose()

                health_output = health_model.run(policy)
                economic_output = economic_model.get_economic_vector(policy)

                loss = self.loss(population_data, health_output, economic_output)
                result = loss_function.Result(solution=policy, loss=loss)
                pareto_frontier.update(result)
                self.record(result)
                step += 1
                if n_steps is not None and step >= n_steps:
                    break
            except StopIteration:
                break

        return pareto_frontier.frontier

    def propose(self) -> lockdown_policy.LockdownTimeSeries:
        """Get a new policy proposal from the config."""
        raise NotImplementedError()

    def record(self, result: loss_function.Result):
        """Possibly record the obtained result."""
        self.results.append(result)


class RandomSearch(Optimizer):  # pylint: disable=too-few-public-methods
    """Optimizer that tries possibilities randomly."""

    def propose(self) -> lockdown_policy.LockdownTimeSeries:
        """Get a new proposal."""
        sample_kwargs = self.config.sample()
        return lockdown_config.LockdownConfig.generate_lockdown_policy(
            sample_kwargs)


class ExhaustiveSearch(Optimizer):
    """Optimizer that tries all possibilities."""

    def __init__(self,
                 config: lockdown_config.LockdownConfig,
                 loss: loss_function.LossFunction):
        """Initialize the search."""
        super().__init__(config, loss)
        self.proposals = self.generate_proposals()

    def propose(self) -> lockdown_policy.LockdownTimeSeries:
        """Get a new proposal."""
        return lockdown_config.LockdownConfig.generate_lockdown_policy(
            next(self.proposals))

    def generate_proposals(self) -> Iterator[
            lockdown_policy.LockdownTimeSeries]:
        """Generator for proposals."""
        range_args = []
        option_args = []

        sample_kwargs = {}
        for name, values in self.config.kwargs.items():
            if isinstance(values, lockdown_config.Options):
                option_args.append((name, values.values))
            elif isinstance(values, lockdown_config.Range):
                range_args.append((name, values))
            else:
                sample_kwargs[name] = values

        option_names = [names for names, _ in option_args]
        cross_product = itertools.product(
            *[values for _, values in option_args])

        for option_values in cross_product:
            for name, value in zip(option_names, option_values):
                sample_kwargs[name] = value
            for range_name, range_arg in range_args:
                sample_kwargs[range_name] = random.uniform(
                    range_arg.min, range_arg.max)
            yield sample_kwargs.copy()
