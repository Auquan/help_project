from help_project.src.optimization import loss_function


def test_pareto_first_update():
    """Test that the first value is stored."""
    pareto = loss_function.ParetoFrontier()
    pareto.update('a', 5)
    assert pareto.frontier == [('a', 5)]


def test_pareto_single_objective_replace():
    """Test that the old value is replaced when a new one dominates it."""
    pareto = loss_function.ParetoFrontier()
    pareto.update('a', 5)
    pareto.update('b', 4)
    assert pareto.frontier == [('b', 4)]


def test_pareto_single_objective_keep():
    """Test that the new value is ditched when it is dominated."""
    pareto = loss_function.ParetoFrontier()
    pareto.update('a', 4)
    pareto.update('b', 5)
    assert pareto.frontier == [('a', 4)]


def test_pareto_multi_objective_replace():
    """Test that the old value is replaced when a new one dominates it."""
    pareto = loss_function.ParetoFrontier()
    pareto.update('a', [5, 5])
    pareto.update('b', [4, 4])
    assert pareto.frontier == [('b', [4, 4])]


def test_pareto_multi_objective_keep():
    """Test that the new value is ditched when it is dominated."""
    pareto = loss_function.ParetoFrontier()
    pareto.update('a', [4, 4])
    pareto.update('b', [5, 5])
    assert pareto.frontier == [('a', [4, 4])]


def test_pareto_multi_objective_accumulate():
    """Test that the when no value dominates, both are kept."""
    pareto = loss_function.ParetoFrontier()
    pareto.update('a', [4, 5])
    pareto.update('b', [5, 4])
    assert pareto.frontier == [('a', [4, 5]),
                               ('b', [5, 4])]
