import csv
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QFileDialog, QHeaderView,
    QAbstractItemView, QCheckBox,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QBrush, QFont

from modbus.models import RegisterData


class RegisterView(QWidget):
    write_requested = Signal(int, int)

    COLUMNS = ["Address", "Type", "Decimal", "Hex", "Binary", "Float", "Signed", "Unsigned", "ASCII"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._registers: dict[int, RegisterData] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search address or value...")
        self._search_input.textChanged.connect(self._apply_filter)
        toolbar.addWidget(QLabel("Search:"))
        toolbar.addWidget(self._search_input)

        self._filter_type = QComboBox()
        self._filter_type.addItems(["All", "Changed Only", "Non-Zero"])
        self._filter_type.currentTextChanged.connect(self._apply_filter)
        toolbar.addWidget(self._filter_type)

        toolbar.addStretch()

        self._export_btn = QPushButton("Export CSV")
        self._export_btn.clicked.connect(self._export_csv)
        toolbar.addWidget(self._export_btn)

        self._clear_btn = QPushButton("Clear Changes")
        self._clear_btn.clicked.connect(self._clear_changes)
        toolbar.addWidget(self._clear_btn)

        layout.addLayout(toolbar)

        self._table = QTableWidget()
        self._table.setColumnCount(len(self.COLUMNS))
        self._table.setHorizontalHeaderLabels(self.COLUMNS)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table)

        self._highlight_color = QColor(100, 180, 100, 80)

    def update_data(self, registers: list[RegisterData]) -> None:
        for reg in registers:
            self._registers[reg.address] = reg
        self._refresh_table()

    def _refresh_table(self) -> None:
        filtered = self._get_filtered_registers()
        self._table.setRowCount(len(filtered))
        bold_font = QFont()
        bold_font.setBold(True)

        for row, reg in enumerate(filtered):
            items = [
                f"{reg.address:04X}",
                "Holding",
                str(reg.value),
                reg.hex_str,
                reg.binary_str,
                reg.float_str,
                reg.signed_str,
                reg.unsigned_str,
                reg.ascii_str,
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                if col == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 2:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                if reg.changed:
                    item.setBackground(self._highlight_color)
                    item.setFont(bold_font)
                self._table.setItem(row, col, item)

        self._table.resizeColumnsToContents()

    def _get_filtered_registers(self) -> list[RegisterData]:
        search = self._search_input.text().strip().lower()
        filter_type = self._filter_type.currentText()
        registers = list(self._registers.values())
        registers.sort(key=lambda r: r.address)

        if filter_type == "Changed Only":
            registers = [r for r in registers if r.changed]
        elif filter_type == "Non-Zero":
            registers = [r for r in registers if r.value != 0]

        if search:
            registers = [
                r for r in registers
                if search in f"{r.address:04X}" or search in str(r.value) or search in r.hex_str.lower()
            ]

        return registers

    def _apply_filter(self) -> None:
        self._refresh_table()

    def _clear_changes(self) -> None:
        for reg in self._registers.values():
            reg.changed = False
        self._refresh_table()

    def _export_csv(self) -> None:
        fpath, _ = QFileDialog.getSaveFileName(self, "Export CSV", "registers.csv", "CSV (*.csv)")
        if not fpath:
            return
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.COLUMNS)
            for addr in sorted(self._registers):
                reg = self._registers[addr]
                writer.writerow([
                    f"{reg.address:04X}", "Holding", reg.value,
                    reg.hex_str, reg.binary_str, reg.float_str,
                    reg.signed_str, reg.unsigned_str, reg.ascii_str,
                ])
