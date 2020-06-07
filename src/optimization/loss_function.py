"""Module for loss functions."""


class LossFunction():
    """A function to evaluate the 'badness' of a given outcome."""

    def compute(self, health_output, economic_output):
        """Compute the loss for a given health and economic output."""
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        """Shortcut to call the compute function."""
        return self.compute(*args, **kwargs)


class ParetoFrontier():
    """Class to store the pareto frontier for a problem."""

    def __init__(self):
        self.frontier = []

    def update(self, point, loss):
        """Update the pareto frontier given a new point and loss value.

        The frontier will remain unchanged if any point dominates the new given
        point. If the new point in turn, dominates any points previously in the
        frontier, these points will be removed."""
        for pareto_point, pareto_loss in self.frontier:
            if pareto_point == point:
                return  # No update - new point already exists.
            if ParetoFrontier.dominate(pareto_loss, loss):
                return  # No update - new loss is worse than some point

        # Update - keep only points that are not dominated by the new point
        self.frontier = [(pareto_point, pareto_loss)
                         for pareto_point, pareto_loss in self.frontier
                         if not ParetoFrontier.dominate(loss, pareto_loss)]
        self.frontier.append((point, loss))

    @classmethod
    def dominate(cls, loss_a, loss_b):
        """Compute whether loss_a dominates loss_b."""
        try:
            return float(loss_a) < float(loss_b)
        except TypeError:
            assert len(loss_a) == len(loss_b), "Losses have different length"
            zipped_values = list(zip(loss_a, loss_b))

            return (any(a < b for a, b in zipped_values) and
                    all(a <= b for a, b in zipped_values))
