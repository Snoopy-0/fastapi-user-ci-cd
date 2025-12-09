import pytest

from app import crud, models

def test_summarize_calculations_empty():
    stats = crud.summarize_calculations([])

    assert stats.total == 0
    assert stats.average_a is None
    assert stats.average_b is None
    assert stats.average_result is None

def test_summarize_calculations_values():
    calculations = [
        models.Calculation(a=2, b=4, result=6, type=models.CalculationType.ADD),
        models.Calculation(a=6, b=2, result=3, type=models.CalculationType.DIVIDE),
    ]

    stats = crud.summarize_calculations(calculations)

    assert stats.total == 2
    assert stats.average_a == pytest.approx(4.0)
    assert stats.average_b == pytest.approx(3.0)
    assert stats.average_result == pytest.approx(4.5)
