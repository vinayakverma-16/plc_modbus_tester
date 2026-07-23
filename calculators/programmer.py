from typing import Optional


class ProgrammerCalculator:
    def __init__(self) -> None:
        self._value: int = 0
        self._word_size: int = 64
        self._last_op: str = ""
        self._last_value: int = 0

    @property
    def value(self) -> int:
        return self._value

    @property
    def word_size(self) -> int:
        return self._word_size

    def set_word_size(self, bits: int) -> None:
        self._word_size = bits
        self._apply_mask()

    def _apply_mask(self) -> None:
        mask = (1 << self._word_size) - 1
        self._value &= mask

    def set_value(self, val: int) -> None:
        self._value = val
        self._apply_mask()

    def input_digit(self, digit: int, base: int) -> None:
        self._value = self._value * base + digit
        self._apply_mask()

    def clear(self) -> None:
        self._value = 0
        self._last_op = ""

    def perform_operation(self, op: str) -> Optional[int]:
        if op == "AND":
            self._last_value = self._value
            self._last_op = op
            return self._value
        if op == "OR":
            self._last_value = self._value
            self._last_op = op
            return self._value
        if op == "XOR":
            self._last_value = self._value
            self._last_op = op
            return self._value
        if op == "NOT":
            self._value = ~self._value
            self._apply_mask()
            return self._value
        if op == "<<" or op == "SHL":
            self._value = (self._value << 1)
            self._apply_mask()
            return self._value
        if op == ">>" or op == "SHR":
            self._value = (self._value >> 1)
            return self._value
        if op == "ROL":
            msb = (self._value >> (self._word_size - 1)) & 1
            self._value = ((self._value << 1) | msb)
            self._apply_mask()
            return self._value
        if op == "ROR":
            lsb = self._value & 1
            self._value = (self._value >> 1) | (lsb << (self._word_size - 1))
            self._apply_mask()
            return self._value
        if op == "=":
            if self._last_op == "AND":
                self._value = self._last_value & self._value
            elif self._last_op == "OR":
                self._value = self._last_value | self._value
            elif self._last_op == "XOR":
                self._value = self._last_value ^ self._value
            self._apply_mask()
            return self._value
        if op == "+":
            self._last_value = self._value
            self._last_op = op
            return self._value
        if op == "-":
            self._last_value = self._value
            self._last_op = op
            return self._value
        if op == "*":
            self._last_value = self._value
            self._last_op = op
            return self._value
        if op == "/":
            self._last_value = self._value
            self._last_op = op
            return self._value
        return None

    def compute_result(self, value: int) -> int:
        if self._last_op == "+":
            return (self._last_value + value) & ((1 << self._word_size) - 1)
        if self._last_op == "-":
            return (self._last_value - value) & ((1 << self._word_size) - 1)
        if self._last_op == "*":
            return (self._last_value * value) & ((1 << self._word_size) - 1)
        if self._last_op == "/":
            if value == 0:
                return 0
            return self._last_value // value
        return value

    def to_hex(self) -> str:
        chars = self._word_size // 4
        return f"{self._value:0{chars}X}"

    def to_bin(self) -> str:
        return f"{self._value:0{self._word_size}b}"

    def to_oct(self) -> str:
        return oct(self._value)[2:]

    def to_dec(self) -> str:
        return str(self._value)
