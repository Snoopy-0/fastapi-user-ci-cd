from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Type


class CalculationType(str, Enum):
    """Supported arithmetic operations."""

    ADD = "add"
    SUBTRACT = "sub"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class CalculationOperation(ABC):
    """Base class for a calculation strategy."""

    calc_type: CalculationType

    @abstractmethod
    def compute(self, a: float, b: float) -> float:
        """Perform the calculation."""


class AddOperation(CalculationOperation):
    calc_type = CalculationType.ADD

    def compute(self, a: float, b: float) -> float:
        return a + b


class SubtractOperation(CalculationOperation):
    calc_type = CalculationType.SUBTRACT

    def compute(self, a: float, b: float) -> float:
        return a - b


class MultiplyOperation(CalculationOperation):
    calc_type = CalculationType.MULTIPLY

    def compute(self, a: float, b: float) -> float:
        return a * b


class DivideOperation(CalculationOperation):
    calc_type = CalculationType.DIVIDE

    def compute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b


_OPERATION_MAP: Dict[CalculationType, Type[CalculationOperation]] = {
    op.calc_type: op
    for op in (AddOperation, SubtractOperation, MultiplyOperation, DivideOperation)
}


def get_operation(calc_type: CalculationType) -> CalculationOperation:
    try:
        operation_cls = _OPERATION_MAP[calc_type]
    except KeyError as exc:
        raise ValueError(f"Unsupported calculation type: {calc_type}") from exc
    return operation_cls()


def execute_calculation(calc_type: CalculationType, a: float, b: float) -> float:
    operation = get_operation(calc_type)
    return operation.compute(a, b)
