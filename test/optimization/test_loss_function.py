"""Test the loss function module."""
from help_project.src.optimization import loss_function


def test_pareto_first_update():
    """Test that the first value is stored."""
    result = loss_function.Result(solution='a', loss=5)
    pareto = loss_function.ParetoFrontier()
    pareto.update(result)
    assert pareto.frontier == [result]


def test_pareto_single_objective_replace():
    """Test that the old value is replaced when a new one dominates it."""
    result_a = loss_function.Result(solution='a', loss=5)
    result_b = loss_function.Result(solution='b', loss=4)
    pareto = loss_function.ParetoFrontier()
    pareto.update(result_a)
    pareto.update(result_b)
    assert pareto.frontier == [result_b]


def test_pareto_single_objective_keep():
    """Test that the new value is ditched when it is dominated."""
    result_a = loss_function.Result(solution='a', loss=4)
    result_b = loss_function.Result(solution='b', loss=5)
    pareto = loss_function.ParetoFrontier()
    pareto.update(result_a)
    pareto.update(result_b)
    assert pareto.frontier == [result_a]


def test_pareto_multi_objective_replace():
    """Test that the old value is replaced when a new one dominates it."""
    result_a = loss_function.Result(solution='a', loss=(5, 5))
    result_b = loss_function.Result(solution='b', loss=(4, 4))
    pareto = loss_function.ParetoFrontier()
    pareto.update(result_a)
    pareto.update(result_b)
    assert pareto.frontier == [result_b]


def test_pareto_multi_objective_keep():
    """Test that the new value is ditched when it is dominated."""
    result_a = loss_function.Result(solution='a', loss=(4, 4))
    result_b = loss_function.Result(solution='b', loss=(5, 5))
    pareto = loss_function.ParetoFrontier()
    pareto.update(result_a)
    pareto.update(result_b)
    assert pareto.frontier == [result_a]


def test_pareto_multi_objective_accumulate():
    """Test that the when no value dominates, both are kept."""
    result_a = loss_function.Result(solution='a', loss=(4, 5))
    result_b = loss_function.Result(solution='b', loss=(5, 4))
    pareto = loss_function.ParetoFrontier()
    pareto.update(result_a)
    pareto.update(result_b)
    assert set(pareto.frontier) == {result_a, result_b}
