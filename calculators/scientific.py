import math
from typing import Optional


class ScientificCalculator:
    def __init__(self) -> None:
        self._current: float = 0.0
        self._memory: float = 0.0
        self._last_op: str = ""
        self._last_value: float = 0.0
        self._new_input: bool = True
        self._angle_mode: str = "DEG"

    @property
    def current(self) -> float:
        return self._current

    @property
    def angle_mode(self) -> str:
        return self._angle_mode

    def set_angle_mode(self, mode: str) -> None:
        self._angle_mode = mode

    def _to_radians(self, v: float) -> float:
        if self._angle_mode == "DEG":
            return math.radians(v)
        if self._angle_mode == "GRAD":
            return v * math.pi / 200.0
        return v

    def _from_radians(self, v: float) -> float:
        if self._angle_mode == "DEG":
            return math.degrees(v)
        if self._angle_mode == "GRAD":
            return v * 200.0 / math.pi
        return v

    def perform_operation(self, op: str, value: Optional[float] = None) -> Optional[str]:
        if value is not None:
            self._current = value
        if op == "sin":
            return self._format_result(math.sin(self._to_radians(self._current)))
        if op == "cos":
            return self._format_result(math.cos(self._to_radians(self._current)))
        if op == "tan":
            return self._format_result(math.tan(self._to_radians(self._current)))
        if op == "asin":
            return self._format_result(self._from_radians(math.asin(max(-1, min(1, self._current)))))
        if op == "acos":
            return self._format_result(self._from_radians(math.acos(max(-1, min(1, self._current)))))
        if op == "atan":
            return self._format_result(self._from_radians(math.atan(self._current)))
        if op == "log":
            if self._current <= 0:
                return "Error"
            return self._format_result(math.log10(self._current))
        if op == "ln":
            if self._current <= 0:
                return "Error"
            return self._format_result(math.log(self._current))
        if op == "exp":
            return self._format_result(math.exp(self._current))
        if op == "10^x":
            return self._format_result(10 ** self._current)
        if op == "x^2":
            return self._format_result(self._current ** 2)
        if op == "x^3":
            return self._format_result(self._current ** 3)
        if op == "x^y":
            self._last_value = self._current
            self._last_op = op
            self._new_input = True
            return self._format_result(self._current)
        if op == "1/x":
            if self._current == 0:
                return "Error"
            return self._format_result(1.0 / self._current)
        if op == "n!":
            if self._current < 0 or self._current != int(self._current):
                return "Error"
            return self._format_result(math.factorial(int(self._current)))
        if op == "pi":
            self._current = math.pi
            self._new_input = True
            return self._format_result(math.pi)
        if op == "e":
            self._current = math.e
            self._new_input = True
            return self._format_result(math.e)
        if op == "=" and self._last_op == "x^y":
            result = self._last_value ** self._current
            self._current = result
            self._new_input = True
            return self._format_result(result)
        return None

    def clear(self) -> str:
        self._current = 0.0
        self._last_op = ""
        self._last_value = 0.0
        self._new_input = True
        return "0"

    def _format_result(self, value: float) -> str:
        if abs(value) > 1e10 or (abs(value) < 1e-10 and value != 0):
            return f"{value:.6e}"
        if value == int(value):
            return str(int(value))
        return f"{value:.10f}".rstrip("0").rstrip(".")
