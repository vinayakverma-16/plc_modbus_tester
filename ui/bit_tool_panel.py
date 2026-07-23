from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLineEdit, QLabel, QSpinBox, QComboBox, QTextEdit,
    QFormLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class BitToolPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._current_value = 0
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        input_group = QGroupBox("Input")
        fl = QFormLayout(input_group)
        self._value_input = QLineEdit("0")
        self._value_input.setFont(QFont("Consolas", 12))
        fl.addRow("Value:", self._value_input)
        self._word_size = QSpinBox()
        self._word_size.setRange(8, 64)
        self._word_size.setValue(16)
        self._word_size.setSingleStep(8)
        fl.addRow("Word Size:", self._word_size)
        self._input_base = QComboBox()
        self._input_base.addItems(["Decimal", "Hex", "Binary"])
        fl.addRow("Base:", self._input_base)
        update_btn = QPushButton("Update")
        update_btn.clicked.connect(self._update_view)
        fl.addRow(update_btn)
        layout.addWidget(input_group)

        bit_group = QGroupBox("Bit Viewer")
        bit_layout = QGridLayout(bit_group)
        for i in range(16):
            lbl = QLabel(str(15 - i))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("Consolas", 7))
            lbl.setStyleSheet("color: #888;")
            bit_layout.addWidget(lbl, 0, i)

        self._bit_buttons: list[QPushButton] = []
        for i in range(64):
            btn = QPushButton("0")
            btn.setFixedSize(34, 26)
            btn.setFont(QFont("Consolas", 8))
            btn.clicked.connect(lambda checked, b=i: self._toggle_bit(b))
            self._bit_buttons.append(btn)
            row = 1 + (i // 16) * 2
            col = i % 16
            bit_layout.addWidget(btn, row, col)
            sep = QLabel("|" if i % 8 == 7 and i % 16 != 15 else "")
            if sep.text():
                sep.setAlignment(Qt.AlignCenter)
                sep.setStyleSheet("color: #555;")
                bit_layout.addWidget(sep, row, col + 1)

        layout.addWidget(bit_group)

        ops_group = QGroupBox("Operations")
        ops_grid = QGridLayout(ops_group)
        ops = [
            ("Shift Left", 0, 0), ("Shift Right", 0, 1),
            ("Byte Swap", 1, 0), ("Word Swap", 1, 1),
            ("Endian Convert", 2, 0), ("NOT", 2, 1),
            ("Mask Generator", 3, 0, 1, 2),
        ]
        for op_info in ops:
            text, r, c = op_info[0], op_info[1], op_info[2]
            colspan = op_info[3] if len(op_info) > 3 else 1
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, t=text: self._perform_op(t))
            ops_grid.addWidget(btn, r, c, 1, colspan)
        layout.addWidget(ops_group)

        self._result_output = QTextEdit()
        self._result_output.setReadOnly(True)
        self._result_output.setFont(QFont("Consolas", 11))
        self._result_output.setMaximumHeight(80)
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(self._result_output)

    def _get_value(self) -> int:
        text = self._value_input.text().strip()
        base = self._input_base.currentText()
        try:
            if base == "Hex":
                return int(text, 16) & ((1 << self._word_size.value()) - 1)
            elif base == "Binary":
                return int(text, 2) & ((1 << self._word_size.value()) - 1)
            else:
                return int(text) & ((1 << self._word_size.value()) - 1)
        except Exception:
            return 0

    def _update_view(self) -> None:
        self._current_value = self._get_value()
        self._refresh_bits()
        self._update_output()

    def _refresh_bits(self) -> None:
        bits = self._word_size.value()
        for i in range(64):
            if i < bits:
                state = (self._current_value >> i) & 1
                self._bit_buttons[i].setText(str(state))
                if state:
                    if i >= bits - 8:
                        color = "#e53935"
                    elif i >= bits - 16:
                        color = "#ff9800"
                    else:
                        color = "#4CAF50"
                    self._bit_buttons[i].setStyleSheet(
                        f"background-color: {color}; color: white; font-weight: bold;"
                    )
                else:
                    self._bit_buttons[i].setStyleSheet(
                        "background-color: #2a2a3a; color: #666;"
                    )
            else:
                self._bit_buttons[i].setText("-")
                self._bit_buttons[i].setStyleSheet("")

    def _toggle_bit(self, bit: int) -> None:
        if bit >= self._word_size.value():
            return
        self._current_value ^= (1 << bit)
        self._refresh_bits()
        self._update_output()

    def _perform_op(self, op: str) -> None:
        val = self._current_value
        bits = self._word_size.value()
        mask = (1 << bits) - 1

        if op == "Shift Left":
            val = (val << 1) & mask
        elif op == "Shift Right":
            val = val >> 1
        elif op == "Byte Swap":
            if bits >= 16:
                high = (val >> 8) & 0xFF
                low = val & 0xFF
                val = ((low << 8) | high) & mask
        elif op == "Word Swap":
            if bits >= 32:
                high = (val >> 16) & 0xFFFF
                low = val & 0xFFFF
                val = ((low << 16) | high) & mask
        elif op == "Endian Convert":
            if bits == 16:
                high = (val >> 8) & 0xFF
                low = val & 0xFF
                val = ((low << 8) | high) & mask
            elif bits == 32:
                b3 = (val >> 24) & 0xFF
                b2 = (val >> 16) & 0xFF
                b1 = (val >> 8) & 0xFF
                b0 = val & 0xFF
                val = ((b0 << 24) | (b1 << 16) | (b2 << 8) | b3) & mask
        elif op == "NOT":
            val = (~val) & mask
        elif op == "Mask Generator":
            self._show_mask_generator()
            return

        self._current_value = val
        self._refresh_bits()
        self._update_output()

    def _show_mask_generator(self) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle("Mask Generator")
        fl = QFormLayout(dlg)
        start = QSpinBox()
        start.setRange(0, self._word_size.value() - 1)
        end = QSpinBox()
        end.setRange(0, self._word_size.value() - 1)
        end.setValue(self._word_size.value() - 1)
        fl.addRow("Start Bit:", start)
        fl.addRow("End Bit:", end)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        fl.addRow(buttons)
        if dlg.exec() == QDialog.Accepted:
            s = min(start.value(), end.value())
            e = max(start.value(), end.value())
            mask = 0
            for i in range(s, e + 1):
                mask |= (1 << i)
            self._result_output.setText(f"Mask: 0x{mask:X}\nBits {s}-{e}")
            self._current_value = mask
            self._refresh_bits()
            self._update_output()

    def _update_output(self) -> None:
        val = self._current_value
        bits = self._word_size.value()
        self._value_input.setText(str(val))
        signed = val if val < (1 << (bits - 1)) else val - (1 << bits)
        text = (
            f"Dec:      {val}\n"
            f"Hex:      0x{val:0{bits // 4}X}\n"
            f"Bin:      {val:0{bits}b}\n"
            f"Signed:   {signed}\n"
            f"Bit count: {val.bit_count()}"
        )
        self._result_output.setText(text)
