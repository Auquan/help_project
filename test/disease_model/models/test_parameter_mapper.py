"""Test the parameter mapper module."""
from help_project.src.disease_model.models import compartment_model
from help_project.src.disease_model.models import parameter_mapper
from help_project.src.exitstrategies import lockdown_policy


def test_fit_and_get():
    """Test that fit and get function properly."""
    mapper = parameter_mapper.ParameterMapper()

    model = compartment_model.CompartmentModel(None)
    policies = [
        lockdown_policy.LockdownPolicy(curfew=1.0),
        lockdown_policy.LockdownPolicy(curfew=0.5),
        lockdown_policy.LockdownPolicy(curfew=0.0),
    ]
    params = [
        {'alpha': 1.0, 'beta': 1.0},
        {'alpha': 0.75, 'beta': 0.5},
        {'alpha': 0.5, 'beta': 0.0},
    ]
    model.parameter_mapper = {
        policies[0]: {'alpha': 1.0, 'beta': 1.0},
        policies[1]: {'alpha': 0.75, 'beta': 0.5},
        policies[2]: {'alpha': 0.5, 'beta': 0.0},
    }
    mapper.fit([model])
    for policy, params in model.parameter_mapper.items():
        assert mapper.get(policy) == params

    test_policy = lockdown_policy.LockdownPolicy(curfew=0.75)
    predicted_params = mapper.get(test_policy)
    assert 0.75 < predicted_params['alpha'] < 1.0
    assert 0.5 < predicted_params['beta'] < 1.0
