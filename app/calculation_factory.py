from abc import ABC, abstractmethod

class Operation(ABC):
    @abstractmethod
    def calculate(self, a: float, b: float) -> float:  # pragma: no cover - abstract
        ...

class AddOperation(Operation):
    def calculate(self, a: float, b: float) -> float:
        return a + b

class SubOperation(Operation):
    def calculate(self, a: float, b: float) -> float:
        return a - b

class MulOperation(Operation):
    def calculate(self, a: float, b: float) -> float:
        return a * b

class DivOperation(Operation):
    def calculate(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("division by zero")
        return a / b

def get_operation(calc_type: str) -> Operation:
    key = calc_type.lower()

    if key == "add":
        return AddOperation()
    if key == "sub":
        return SubOperation()
    if key in ("mul", "multiply"):
        return MulOperation()
    if key in ("div", "divide"):
        return DivOperation()

    raise ValueError(f"Unsupported calculation type: {calc_type}")
