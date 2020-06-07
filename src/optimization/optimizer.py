"""Module for handling the optimization loop."""
import itertools
import random

from help_project.src.optimization import loss_function
from help_project.src.optimization import lockdown_config


class Optimizer():
    """Main optimization class."""

    def __init__(self, config, loss):
        self.config = config
        self.loss = loss

    def optimize(self, health_model, economic_model, n_steps=None):
        """Run the optimization loop."""
        pareto_frontier = loss_function.ParetoFrontier()

        step = 0
        while True:
            try:
                policy = self.propose()

                health_output = health_model.run(policy)
                economic_output = economic_model.run(policy)

                loss = self.loss(health_output, economic_output)
                self.record(policy, loss)

                pareto_frontier.update(policy, loss)
                step += 1
                if n_steps is not None and step >= n_steps:
                    break
            except StopIteration:
                break

        return pareto_frontier.frontier

    def propose(self):
        """Get a new policy proposal from the config."""
        raise NotImplementedError()

    def record(self, proposal, loss):
        """Record the loss for the given proposal."""
        raise NotImplementedError()


class RandomSearch(Optimizer):
    """Optimizer that tries possibilities randomly."""

    def propose(self):
        """Get a new proposal."""
        sample_kwargs = self.config.sample()
        return lockdown_config.LockdownConfig.generate_lockdown_policy(
            sample_kwargs)

    def record(self, proposal, loss):
        """Do nothing."""
        return


class ExhaustiveSearch(Optimizer):
    """Optimizer that tries all possibilities."""

    def __init__(self, config, loss):
        super().__init__(config, loss)
        self.proposals = self.generate_proposals()

    def propose(self):
        """Get a new proposal."""
        return next(self.proposals)

    def record(self, proposal, loss):
        """Do nothing."""
        return

    def generate_proposals(self):
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
