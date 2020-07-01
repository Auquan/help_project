"""Test for base model module."""
from help_project.src.disease_model import parameter


def test_param_default():
    """Test that a parameter's default attributes are set up correctly."""
    param = parameter.Parameter(
        name='a',
        description='A parameter')
    assert param.bounds is None
    assert param.policy_dependent is False


def test_config_parse():
    """Test that parse converts a list to a dict correctly."""
    config = parameter.ParameterConfig(
        parameter.Parameter(name='a',
                            description='A parameter',
                            bounds=[0, 5]),
        parameter.Parameter(name='b',
                            description='Another parameter',
                            bounds=[0, 1]),
    )
    assert config.parse([2, 1]) == {'a': 2, 'b': 1}

def test_config_flatten():
    """Test that parse converts a dict to a list correctly."""
    config = parameter.ParameterConfig(
        parameter.Parameter(name='a',
                            description='A parameter',
                            bounds=[0, 5]),
        parameter.Parameter(name='b',
                            description='Another parameter',
                            bounds=[0, 1]),
    )
    assert config.flatten({'a': 2, 'b': 1}) == [2, 1]
