from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QPushButton, QLineEdit, QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from calculators.standard import StandardCalculator
from calculators.scientific import ScientificCalculator
from calculators.programmer import ProgrammerCalculator


class CalculatorPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._tabs = QTabWidget()
        self._tabs.addTab(StandardCalcWidget(), "Standard")
        self._tabs.addTab(ScientificCalcWidget(), "Scientific")
        self._tabs.addTab(ProgrammerCalcWidget(), "Programmer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self._tabs)


class StandardCalcWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._calc = StandardCalculator()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._display = QLineEdit("0")
        self._display.setReadOnly(True)
        self._display.setAlignment(Qt.AlignRight)
        font = QFont("Consolas", 14)
        self._display.setFont(font)
        layout.addWidget(self._display)

        grid = QGridLayout()
        buttons = [
            ("MC", 0, 0), ("MR", 0, 1), ("M+", 0, 2), ("M-", 0, 3), ("MS", 0, 4),
            ("%", 1, 0), ("CE", 1, 1), ("C", 1, 2), ("<-", 1, 3), ("/", 1, 4),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("*", 2, 3), ("1/x", 2, 4),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("-", 3, 3), ("sqrt", 3, 4),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("+", 4, 3), ("+/-", 4, 4),
            ("0", 5, 0, 1, 2), (".", 5, 2), ("=", 5, 3, 1, 2),
        ]
        for btn_info in buttons:
            text = btn_info[0]
            r, c = btn_info[1], btn_info[2]
            rowspan = btn_info[3] if len(btn_info) > 3 else 1
            colspan = btn_info[4] if len(btn_info) > 4 else 1
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, t=text: self._on_button(t))
            if text in ("=",):
                btn.setStyleSheet("font-weight: bold;")
            grid.addWidget(btn, r, c, rowspan, colspan)

        layout.addLayout(grid)

        self._current_text = "0"

    def _on_button(self, text: str) -> None:
        if text.isdigit():
            self._current_text = self._calc.append_digit(self._current_text, text)
        elif text == ".":
            self._current_text = self._calc.append_decimal(self._current_text)
        else:
            result = self._calc.perform_operation(text)
            if result is not None:
                self._current_text = result
        self._display.setText(self._current_text)


class ScientificCalcWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._calc = ScientificCalculator()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._display = QLineEdit("0")
        self._display.setReadOnly(True)
        self._display.setAlignment(Qt.AlignRight)
        font = QFont("Consolas", 12)
        self._display.setFont(font)
        layout.addWidget(self._display)

        grid = QGridLayout()
        buttons = [
            ("sin", 0, 0), ("cos", 0, 1), ("tan", 0, 2), ("log", 0, 3), ("ln", 0, 4),
            ("asin", 1, 0), ("acos", 1, 1), ("atan", 1, 2), ("10^x", 1, 3), ("exp", 1, 4),
            ("x^2", 2, 0), ("x^3", 2, 1), ("x^y", 2, 2), ("n!", 2, 3), ("1/x", 2, 4),
            ("7", 3, 0), ("8", 3, 1), ("9", 3, 2), ("pi", 3, 3), ("e", 3, 4),
            ("4", 4, 0), ("5", 4, 1), ("6", 4, 2), ("(", 4, 3), (")", 4, 4),
            ("1", 5, 0), ("2", 5, 1), ("3", 5, 2), ("C", 5, 3), ("<-", 5, 4),
            ("0", 6, 0, 1, 2), (".", 6, 2), ("=", 6, 3, 1, 2),
        ]
        for btn_info in buttons:
            text = btn_info[0]
            r, c = btn_info[1], btn_info[2]
            rowspan = btn_info[3] if len(btn_info) > 3 else 1
            colspan = btn_info[4] if len(btn_info) > 4 else 1
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, t=text: self._on_button(t))
            grid.addWidget(btn, r, c, rowspan, colspan)

        layout.addLayout(grid)
        self._current_text = "0"

    def _on_button(self, text: str) -> None:
        if text.isdigit():
            if self._current_text == "0":
                self._current_text = text
            else:
                self._current_text += text
        elif text == ".":
            if "." not in self._current_text:
                self._current_text += "."
        elif text == "C":
            self._current_text = self._calc.clear()
        elif text == "<-":
            self._current_text = self._current_text[:-1] or "0"
        else:
            try:
                val = float(self._current_text)
                result = self._calc.perform_operation(text, val)
                if result is not None:
                    self._current_text = result
            except ValueError:
                self._current_text = "Error"
        self._display.setText(self._current_text)


class ProgrammerCalcWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._calc = ProgrammerCalculator()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._display = QLineEdit("0")
        self._display.setReadOnly(True)
        self._display.setAlignment(Qt.AlignRight)
        font = QFont("Consolas", 14)
        self._display.setFont(font)
        layout.addWidget(self._display)

        base_layout = QHBoxLayout()
        self._hex_radio = QPushButton("HEX")
        self._dec_radio = QPushButton("DEC")
        self._oct_radio = QPushButton("OCT")
        self._bin_radio = QPushButton("BIN")
        for b in (self._hex_radio, self._dec_radio, self._oct_radio, self._bin_radio):
            b.setCheckable(True)
            b.clicked.connect(lambda checked, bb=b: self._set_base(bb))
            base_layout.addWidget(b)
        self._dec_radio.setChecked(True)
        self._current_base = 10
        layout.addLayout(base_layout)

        grid = QGridLayout()
        buttons = [
            ("AND", 0, 0), ("OR", 0, 1), ("XOR", 0, 2), ("NOT", 0, 3),
            ("SHL", 1, 0), ("SHR", 1, 1), ("ROL", 1, 2), ("ROR", 1, 3),
            ("A", 2, 0), ("B", 2, 1), ("C", 2, 2), ("D", 2, 3),
            ("E", 3, 0), ("F", 3, 1), ("C", 3, 2), ("=", 3, 3),
            ("7", 4, 0), ("8", 4, 1), ("9", 4, 2), ("+", 4, 3),
            ("4", 5, 0), ("5", 5, 1), ("6", 5, 2), ("-", 5, 3),
            ("1", 6, 0), ("2", 6, 1), ("3", 6, 2), ("*", 6, 3),
            ("0", 7, 0), ("<-", 7, 1), ("Clear", 7, 2), ("/", 7, 3),
        ]
        for btn_info in buttons:
            text = btn_info[0]
            r, c = btn_info[1], btn_info[2]
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, t=text: self._on_button(t))
            grid.addWidget(btn, r, c)

        layout.addLayout(grid)
        self._update_display()

    def _set_base(self, btn) -> None:
        for b in (self._hex_radio, self._dec_radio, self._oct_radio, self._bin_radio):
            b.setChecked(b == btn)
        base_map = {self._hex_radio: 16, self._dec_radio: 10, self._oct_radio: 8, self._bin_radio: 2}
        self._current_base = base_map.get(btn, 10)
        self._update_display()

    def _update_display(self) -> None:
        base_map = {16: self._calc.to_hex, 10: self._calc.to_dec, 8: self._calc.to_oct, 2: self._calc.to_bin}
        formatter = base_map.get(self._current_base, self._calc.to_dec)
        self._display.setText(formatter())

    def _on_button(self, text: str) -> None:
        valid_hex = set("0123456789ABCDEF")
        valid_dec = set("0123456789")
        valid_oct = set("01234567")
        valid_bin = set("01")
        base_valid = {16: valid_hex, 10: valid_dec, 8: valid_oct, 2: valid_bin}
        allowed = base_valid.get(self._current_base, valid_dec)

        if text in allowed:
            self._calc.input_digit(int(text, 16), self._current_base)
        elif text == "<-":
            self._calc.set_value(self._calc.value >> 1)
        elif text == "Clear":
            self._calc.clear()
        elif text == "=":
            result = self._calc.perform_operation(text)
            if result is not None:
                pass
        else:
            self._calc.perform_operation(text)
        self._update_display()
