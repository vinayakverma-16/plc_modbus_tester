from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QPushButton, QTextEdit, QComboBox, QLineEdit, QLabel, QTabWidget,
    QGridLayout,
)
from PySide6.QtGui import QFont

from converters.numeric import NumericConverter
from converters.ieee754 import IEEE754Converter
from converters.ascii import ASCIIConverter
from converters.crc import CRCConverter


class ConverterPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        tabs = QTabWidget()
        tabs.addTab(NumericConvertTab(), "Numeric")
        tabs.addTab(IEEE754Tab(), "IEEE754")
        tabs.addTab(AsciiConvertTab(), "ASCII/UTF-8")
        tabs.addTab(CRCTab(), "CRC")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(tabs)


class NumericConvertTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self._input = QTextEdit()
        self._input.setPlaceholderText("Enter value...")
        self._input.setMaximumHeight(60)
        font = QFont("Consolas", 11)
        self._input.setFont(font)
        layout.addWidget(QLabel("Input:"))
        layout.addWidget(self._input)

        grid = QGridLayout()
        self._from_base = QComboBox()
        self._from_base.addItems(["Decimal", "Hex", "Binary", "Octal"])
        grid.addWidget(QLabel("From:"), 0, 0)
        grid.addWidget(self._from_base, 0, 1)
        self._to_base = QComboBox()
        self._to_base.addItems(["Decimal", "Hex", "Binary", "Octal"])
        self._to_base.setCurrentText("Hex")
        grid.addWidget(QLabel("To:"), 1, 0)
        grid.addWidget(self._to_base, 1, 1)
        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(self._convert)
        grid.addWidget(convert_btn, 2, 0, 1, 2)
        layout.addLayout(grid)

        self._signed_btn = QPushButton("Signed -> Unsigned")
        self._signed_btn.clicked.connect(self._signed_convert)
        layout.addWidget(self._signed_btn)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        font = QFont("Consolas", 12)
        self._output.setFont(font)
        layout.addWidget(QLabel("Result:"))
        layout.addWidget(self._output)

    def _convert(self) -> None:
        text = self._input.toPlainText().strip()
        if not text:
            return
        base_map = {"Decimal": 10, "Hex": 16, "Binary": 2, "Octal": 8}
        from_b = base_map[self._from_base.currentText()]
        to_b = base_map[self._to_base.currentText()]
        try:
            if to_b == 10:
                result = NumericConverter.to_dec(text, from_b)
            elif to_b == 16:
                result = NumericConverter.to_hex(text, from_b)
            elif to_b == 2:
                result = NumericConverter.to_bin(text, from_b)
            elif to_b == 8:
                result = NumericConverter.to_oct(text, from_b)
            self._output.setText(result)
        except Exception:
            self._output.setText("Error")

    def _signed_convert(self) -> None:
        text = self._input.toPlainText().strip()
        if not text:
            return
        try:
            val = int(text)
            unsigned = NumericConverter.signed_to_unsigned(val, 16)
            self._output.setText(f"Signed: {val}\nUnsigned: {unsigned}")
        except Exception:
            self._output.setText("Error")


class IEEE754Tab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        float_group = QGroupBox("Float (32-bit)")
        fl = QFormLayout(float_group)
        self._float_input = QLineEdit()
        self._float_input.setPlaceholderText("e.g. 3.14")
        fl.addRow("Float:", self._float_input)
        self._float_hex = QLineEdit()
        self._float_hex.setReadOnly(True)
        fl.addRow("Hex:", self._float_hex)
        float_to_btn = QPushButton("Float -> Hex")
        float_to_btn.clicked.connect(self._float_to_hex)
        fl.addRow(float_to_btn)
        self._hex_to_float_input = QLineEdit()
        self._hex_to_float_input.setPlaceholderText("e.g. 4048F5C3")
        fl.addRow("Hex:", self._hex_to_float_input)
        self._float_result = QLineEdit()
        self._float_result.setReadOnly(True)
        fl.addRow("Float:", self._float_result)
        hex_to_btn = QPushButton("Hex -> Float")
        hex_to_btn.clicked.connect(self._hex_to_float)
        fl.addRow(hex_to_btn)
        layout.addWidget(float_group)

        double_group = QGroupBox("Double (64-bit)")
        dl = QFormLayout(double_group)
        self._double_input = QLineEdit()
        self._double_input.setPlaceholderText("e.g. 3.14159265358979")
        dl.addRow("Double:", self._double_input)
        self._double_hex = QLineEdit()
        self._double_hex.setReadOnly(True)
        dl.addRow("Hex:", self._double_hex)
        double_to_btn = QPushButton("Double -> Hex")
        double_to_btn.clicked.connect(self._double_to_hex)
        dl.addRow(double_to_btn)
        layout.addWidget(double_group)

        layout.addStretch()

    def _float_to_hex(self) -> None:
        try:
            val = float(self._float_input.text())
            self._float_hex.setText(IEEE754Converter.float_to_hex(val))
        except Exception:
            self._float_hex.setText("Error")

    def _hex_to_float(self) -> None:
        try:
            val = IEEE754Converter.hex_to_float(self._hex_to_float_input.text())
            self._float_result.setText(str(val))
        except Exception:
            self._float_result.setText("Error")

    def _double_to_hex(self) -> None:
        try:
            val = float(self._double_input.text())
            self._double_hex.setText(IEEE754Converter.double_to_hex(val))
        except Exception:
            self._double_hex.setText("Error")


class AsciiConvertTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self._input = QTextEdit()
        self._input.setPlaceholderText("Enter text or hex...")
        self._input.setMaximumHeight(80)
        font = QFont("Consolas", 11)
        self._input.setFont(font)
        layout.addWidget(QLabel("Input:"))
        layout.addWidget(self._input)

        grid = QGridLayout()
        btn1 = QPushButton("Text -> Hex")
        btn1.clicked.connect(lambda: self._convert("text_to_hex"))
        grid.addWidget(btn1, 0, 0)
        btn2 = QPushButton("Hex -> Text")
        btn2.clicked.connect(lambda: self._convert("hex_to_text"))
        grid.addWidget(btn2, 0, 1)
        btn3 = QPushButton("Text -> UTF-8 Hex")
        btn3.clicked.connect(lambda: self._convert("text_to_utf8"))
        grid.addWidget(btn3, 1, 0)
        btn4 = QPushButton("UTF-8 Hex -> Text")
        btn4.clicked.connect(lambda: self._convert("utf8_to_text"))
        grid.addWidget(btn4, 1, 1)
        btn5 = QPushButton("Text -> Binary")
        btn5.clicked.connect(lambda: self._convert("text_to_bin"))
        grid.addWidget(btn5, 2, 0)
        btn6 = QPushButton("Binary -> Text")
        btn6.clicked.connect(lambda: self._convert("bin_to_text"))
        grid.addWidget(btn6, 2, 1)
        layout.addLayout(grid)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        font = QFont("Consolas", 11)
        self._output.setFont(font)
        layout.addWidget(QLabel("Result:"))
        layout.addWidget(self._output)

    def _convert(self, mode: str) -> None:
        text = self._input.toPlainText().strip()
        if not text:
            return
        try:
            if mode == "text_to_hex":
                self._output.setText(ASCIIConverter.text_to_hex(text))
            elif mode == "hex_to_text":
                self._output.setText(ASCIIConverter.hex_to_text(text))
            elif mode == "text_to_utf8":
                self._output.setText(ASCIIConverter.text_to_utf8_hex(text))
            elif mode == "utf8_to_text":
                self._output.setText(ASCIIConverter.utf8_hex_to_text(text))
            elif mode == "text_to_bin":
                self._output.setText(ASCIIConverter.text_to_bin(text))
            elif mode == "bin_to_text":
                self._output.setText(ASCIIConverter.bin_to_text(text))
        except Exception:
            self._output.setText("Error")


class CRCTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self._input = QTextEdit()
        self._input.setPlaceholderText("Enter hex data (e.g. 01 03 00 00 00 0A)")
        self._input.setMaximumHeight(80)
        font = QFont("Consolas", 11)
        self._input.setFont(font)
        layout.addWidget(QLabel("Hex Data:"))
        layout.addWidget(self._input)

        grid = QGridLayout()
        btn1 = QPushButton("CRC-16 Modbus")
        btn1.clicked.connect(self._calc_crc16)
        grid.addWidget(btn1, 0, 0)
        btn2 = QPushButton("CRC-32")
        btn2.clicked.connect(self._calc_crc32)
        grid.addWidget(btn2, 0, 1)
        btn3 = QPushButton("Verify CRC-16")
        btn3.clicked.connect(self._verify_crc16)
        grid.addWidget(btn3, 1, 0, 1, 2)
        layout.addLayout(grid)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        font = QFont("Consolas", 12)
        self._output.setFont(font)
        layout.addWidget(QLabel("Result:"))
        layout.addWidget(self._output)

    def _calc_crc16(self) -> None:
        try:
            data = CRCConverter.hex_string_to_bytes(self._input.toPlainText().strip())
            crc = CRCConverter.crc16_modbus(data)
            self._output.setText(f"CRC-16: {crc:04X}\nFull packet: {self._input.toPlainText().strip()} {crc:04X}")
        except Exception:
            self._output.setText("Error")

    def _calc_crc32(self) -> None:
        try:
            data = CRCConverter.hex_string_to_bytes(self._input.toPlainText().strip())
            crc = CRCConverter.crc32(data)
            self._output.setText(f"CRC-32: {crc}")
        except Exception:
            self._output.setText("Error")

    def _verify_crc16(self) -> None:
        try:
            valid = CRCConverter.verify_crc16(self._input.toPlainText().strip())
            self._output.setText("CRC: Valid" if valid else "CRC: Invalid")
        except Exception:
            self._output.setText("Error")
