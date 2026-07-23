from typing import Optional


class StandardCalculator:
    def __init__(self) -> None:
        self._current: float = 0.0
        self._memory: float = 0.0
        self._last_op: str = ""
        self._last_value: float = 0.0
        self._new_input: bool = True

    @property
    def current(self) -> float:
        return self._current

    def input_digit(self, digit: str) -> None:
        pass

    def input_decimal(self) -> None:
        pass

    def perform_operation(self, op: str) -> Optional[str]:
        if op == "C":
            self._current = 0.0
            self._last_op = ""
            self._last_value = 0.0
            self._new_input = True
            return "0"
        if op == "CE":
            self._current = 0.0
            self._new_input = True
            return "0"
        if op == "=":
            if self._last_op == "+":
                self._current = self._last_value + self._current
            elif self._last_op == "-":
                self._current = self._last_value - self._current
            elif self._last_op == "*":
                self._current = self._last_value * self._current
            elif self._last_op == "/":
                if self._current == 0:
                    return "Error"
                self._current = self._last_value / self._current
            self._new_input = True
            return self._format_result(self._current)
        if op in ("+", "-", "*", "/"):
            self._last_value = self._current
            self._last_op = op
            self._new_input = True
            return self._format_result(self._current)
        if op == "MS":
            self._memory = self._current
        elif op == "MR":
            self._current = self._memory
            return self._format_result(self._current)
        elif op == "MC":
            self._memory = 0.0
        elif op == "M+":
            self._memory += self._current
        elif op == "M-":
            self._memory -= self._current
        elif op == "+/-":
            self._current = -self._current
            return self._format_result(self._current)
        elif op == "%":
            self._current = self._current / 100.0
            return self._format_result(self._current)
        elif op == "1/x":
            if self._current == 0:
                return "Error"
            self._current = 1.0 / self._current
            return self._format_result(self._current)
        elif op == "sqrt":
            if self._current < 0:
                return "Error"
            import math
            self._current = math.sqrt(self._current)
            return self._format_result(self._current)
        return None

    def _format_result(self, value: float) -> str:
        if value == int(value):
            return str(int(value))
        return f"{value:.10f}".rstrip("0").rstrip(".")

    def append_digit(self, current_text: str, digit: str) -> str:
        if self._new_input:
            self._current = 0.0
            self._new_input = False
            current_text = "0"
        if current_text == "0" and digit != ".":
            current_text = digit
        else:
            current_text += digit
        self._current = float(current_text)
        return current_text

    def append_decimal(self, current_text: str) -> str:
        if self._new_input:
            self._current = 0.0
            self._new_input = False
            current_text = "0"
        if "." not in current_text:
            current_text += "."
        return current_text
