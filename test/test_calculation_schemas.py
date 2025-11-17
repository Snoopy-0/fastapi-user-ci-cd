import pytest
from pydantic import ValidationError

from app.schemas import CalculationCreate, CalculationType

def test_calculation_create_valid_add():
    calc = CalculationCreate(a=2, b=3, type="Add")
    assert calc.type == CalculationType.add
    assert calc.type.value == "add"

def test_calculation_create_division_by_zero():
    with pytest.raises(ValidationError):
        CalculationCreate(a=1, b=0, type="Divide")
