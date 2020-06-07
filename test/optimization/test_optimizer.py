from help_project.src.optimization import lockdown_config
from help_project.src.optimization import loss_function
from help_project.src.optimization import optimizer


class MockHealthModel():
    """Mock health model."""
    def run(self, policy):
        if policy['strategy'] == 1:
            return 1
        elif policy['strategy'] == 2:
            return 2
        elif policy['strategy'] == 3:
            return 5


class MockEconomicModel():
    """Mock economic model."""
    def run(self, policy):
        if policy['strategy'] == 1:
            return 5
        elif policy['strategy'] == 2:
            return 2
        elif policy['strategy'] == 3:
            return 1


class WeightedLoss(loss_function.LossFunction):
    """Weighted Loss."""

    def __init__(self, health_weight, economic_weight):
        self.health_weight = health_weight
        self.economic_weight = economic_weight

    def compute(self, health_output, economic_output):
        """Compute the loss for a given health and economic output."""
        return (self.health_weight * health_output +
                self.economic_weight * economic_output)


class MultiLoss(loss_function.LossFunction):
    """Multi objective Loss."""

    def compute(self, health_output, economic_output):
        """Compute the loss for a given health and economic output."""
        return (health_output, economic_output)


def test_optimize_single_objective_exhaustive_search():
    """Test that exhaustive search fidns the optimum value."""
    opt = optimizer.ExhaustiveSearch(
        config=lockdown_config.LockdownConfig(
            strategy=lockdown_config.Options([1, 2, 3]),
        ),
        loss=WeightedLoss(1, 1),
    )
    solution = opt.optimize(
        health_model=MockHealthModel(),
        economic_model=MockEconomicModel(),
    )
    assert solution == [({'strategy': 2}, 4)]


def test_optimize_single_objective_random_search():
    """Test that random search finds the optimum value."""
    opt = optimizer.RandomSearch(
        config=lockdown_config.LockdownConfig(
            strategy=lockdown_config.Options([1, 2, 3]),
        ),
        loss=WeightedLoss(1, 1),
    )
    solution = opt.optimize(
        health_model=MockHealthModel(),
        economic_model=MockEconomicModel(),
        n_steps=100,
    )
    assert solution == [({'strategy': 2}, 4)]


def test_optimize_multi_objective_exhaustive_search():
    """Test that exhaustive search fidns the optimum value."""
    opt = optimizer.ExhaustiveSearch(
        config=lockdown_config.LockdownConfig(
            strategy=lockdown_config.Options([1, 2, 3]),
        ),
        loss=MultiLoss())
    solution = opt.optimize(
        health_model=MockHealthModel(),
        economic_model=MockEconomicModel(),
    )
    assert solution == [({'strategy': 1}, (1, 5)),
                        ({'strategy': 2}, (2, 2)),
                        ({'strategy': 3}, (5, 1))]
