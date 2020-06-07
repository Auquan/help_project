from help_project.src.optimization import lockdown_config


def test_kwargs_sample():
    """Test whether sample works as expected."""
    config = lockdown_config.LockdownConfig(
        a=lockdown_config.Options([1, 2, 3]),
        b=5,
        c='param',
        x=lockdown_config.Range(1, 10),
    )
    sample_kwargs = config.sample()
    assert sample_kwargs['a'] in [1, 2, 3]
    assert sample_kwargs['b'] == 5
    assert sample_kwargs['c'] == 'param'
    assert 1 <= sample_kwargs['x'] <= 10
