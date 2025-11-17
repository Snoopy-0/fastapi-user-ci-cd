import pytest

from app.calculation_factory import (
    get_operation,
    AddOperation,
    SubOperation,
    MulOperation,
    DivOperation,
)

def test_factory_returns_correct_operation_class():
    assert isinstance(get_operation("add"), AddOperation)
    assert isinstance(get_operation("sub"), SubOperation)
    assert isinstance(get_operation("mul"), MulOperation)
    assert isinstance(get_operation("div"), DivOperation)

def test_add_operation():
    op = get_operation("add")
    assert op.calculate(1, 2) == 3

def test_sub_operation():
    op = get_operation("sub")
    assert op.calculate(5, 3) == 2

def test_mul_operation():
    op = get_operation("mul")
    assert op.calculate(2, 4) == 8

def test_div_operation():
    op = get_operation("div")
    assert op.calculate(10, 2) == 5

def test_div_operation_zero_division():
    op = get_operation("div")
    with pytest.raises(ZeroDivisionError):
        op.calculate(1, 0)
