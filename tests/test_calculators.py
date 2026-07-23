import pytest
from calculators.standard import StandardCalculator
from calculators.scientific import ScientificCalculator
from calculators.programmer import ProgrammerCalculator


class TestStandardCalculator:
    def test_addition(self) -> None:
        calc = StandardCalculator()
        calc.perform_operation("+")
        calc.perform_operation("=")
        assert calc.current == 0.0

    def test_clear(self) -> None:
        calc = StandardCalculator()
        calc.perform_operation("C")
        assert calc.current == 0.0

    def test_division_by_zero(self) -> None:
        calc = StandardCalculator()
        calc.perform_operation("/")
        result = calc.perform_operation("=")
        assert result == "Error"


class TestScientificCalculator:
    def test_sin(self) -> None:
        calc = ScientificCalculator()
        import math
        result = calc.perform_operation("sin", 90.0)
        assert result is not None
        assert abs(float(result) - 1.0) < 0.001

    def test_pi(self) -> None:
        calc = ScientificCalculator()
        import math
        result = calc.perform_operation("pi")
        assert result is not None
        assert abs(float(result) - math.pi) < 0.001

    def test_clear(self) -> None:
        calc = ScientificCalculator()
        result = calc.clear()
        assert result == "0"


class TestProgrammerCalculator:
    def test_hex(self) -> None:
        calc = ProgrammerCalculator()
        calc.set_word_size(16)
        calc.set_value(255)
        assert calc.to_hex() == "00FF"

    def test_bin(self) -> None:
        calc = ProgrammerCalculator()
        calc.set_value(10)
        assert calc.to_bin()[-4:] == "1010"

    def test_word_size(self) -> None:
        calc = ProgrammerCalculator()
        calc.set_word_size(8)
        calc.set_value(256)
        assert calc.value == 0

    def test_not(self) -> None:
        calc = ProgrammerCalculator()
        calc.set_value(0)
        calc.perform_operation("NOT")
        assert calc.value != 0
