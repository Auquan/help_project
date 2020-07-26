"""Module containing a learnable parameter mapper for compartment models."""
import attr
import numpy as np
from sklearn import neighbors


class ParameterMapper():
    """A learnable parameter mapper for compartment models.

    The mapper uses KNN internally to map policies to parameter values.
    """

    def __init__(self, n_neighbors: int = 3, weights: str = 'distance'):
        self.knn = neighbors.KNeighborsRegressor(
            n_neighbors=n_neighbors,
            weights=weights)
        self.param_keys = []

    def fit(self, models):
        """Fit to the given models.

        The models must already have been fit to the data.
        """
        # pylint: disable=invalid-name
        x = []
        y = []
        for model in models:
            for policy, params in model.parameter_mapper.items():
                x.append(
                    np.array(list(attr.asdict(policy).values())))
                y.append(list(params.values()))
        self.knn.fit(x, y)
        self.param_keys = list(models[0].parameter_mapper.values())[0].keys()


    def get(self, policy):
        """Get the parameters for the policy."""
        # pylint: disable=invalid-name
        x = np.array(list(attr.asdict(policy).values()))
        y = self.knn.predict([x])
        return dict(zip(self.param_keys, y[0]))
