"""Module for model parameter definition."""
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Tuple
import attr


@attr.s
class Parameter:  # pylint: disable=too-few-public-methods
    """Struct for holding a parameter."""
    name: str = attr.ib()
    description: str = attr.ib()
    bounds: Optional[Tuple[float, float]] = attr.ib()


class ParameterConfig:
    """Class for handling a list of parameters."""

    def __init__(self, *parameters: Sequence[Parameter]):
        """Initialize the config.

        Args:
            *parameters: The parameters that are part of this config.
        """
        self.parameters = parameters

    def flatten(self, values: Dict[str, float]):
        """Transform a dictionary of parameter values to a tuple."""
        return [values[parameter.name] for parameter in self.parameters]

    def parse(self, values: Sequence):
        """Transform a tuple of parameter values to a dictionary."""
        return {
            parameter.name: value
            for parameter, value in zip(self.parameters, values)
        }

    def __iter__(self):
        return iter(self.parameters)
