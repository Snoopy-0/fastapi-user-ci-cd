import pytest

from app.calculations import (
    CalculationType,
    execute_calculation,
    get_operation,
)

def test_execute_calculation_operations():
    assert execute_calculation(CalculationType.ADD, 2, 3) == 5
    assert execute_calculation(CalculationType.SUBTRACT, 7, 3) == 4
    assert execute_calculation(CalculationType.MULTIPLY, 4, 2.5) == 10
    assert execute_calculation(CalculationType.DIVIDE, 20, 5) == 4

def test_division_by_zero_raises():
    with pytest.raises(ValueError):
        execute_calculation(CalculationType.DIVIDE, 5, 0)

def test_get_operation_invalid_type():
    with pytest.raises(ValueError):
        get_operation("mod")  # type: ignore[arg-type]
