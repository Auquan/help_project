"""Module containing the LockdownConfig class."""
import collections
import random


class LockdownConfig():
    """Class for generating valid lockdown policies."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def sample(self):
        """Return a sample lockdown policy."""
        sample_kwargs = {}
        for name, values in self.kwargs.items():
            if isinstance(values, Options):
                value = random.sample(values.values, 1)[0]
            elif isinstance(values, Range):
                value = random.uniform(values.min, values.max)
            else:
                value = values
            sample_kwargs[name] = value
        return sample_kwargs

    @classmethod
    def generate_lockdown_policy(cls, kwargs):
        """Generate the actual policy."""
        return kwargs  # TODO: Adapt to group 2 code.


Options = collections.namedtuple('Options', 'values')
Range = collections.namedtuple('Range', 'min, max')
