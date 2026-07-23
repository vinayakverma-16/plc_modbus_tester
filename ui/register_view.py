import csv
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QFileDialog, QHeaderView,
    QAbstractItemView, QMenu, QApplication, QInputDialog,
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QColor, QFont

from modbus.models import RegisterData


class RegisterView(QWidget):
    write_requested = Signal(int, int)
    add_to_chart_requested = Signal(int)

    COLUMNS = ["Address", "Type", "Decimal", "Hex", "Binary", "Float", "Signed", "Unsigned", "ASCII"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._registers: dict[int, RegisterData] = {}
        self._flash_addresses: set[int] = set()

        self._flash_timer = QTimer(self)
        self._flash_timer.setInterval(400)
        self._flash_timer.timeout.connect(self._clear_flash)

        self._flash_color = QColor(255, 220, 50, 120)
        self._changed_color = QColor(100, 180, 100, 80)

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

        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        self._table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.horizontalHeader().customContextMenuRequested.connect(self._header_context_menu)

        layout.addWidget(self._table)

    def update_data(self, registers: list[RegisterData]) -> None:
        for reg in registers:
            self._registers[reg.address] = reg
            if reg.changed:
                self._flash_addresses.add(reg.address)
        if self._flash_addresses:
            self._flash_timer.start()
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
                if reg.address in self._flash_addresses:
                    item.setBackground(self._flash_color)
                    item.setFont(bold_font)
                elif reg.changed:
                    item.setBackground(self._changed_color)
                    item.setFont(bold_font)
                self._table.setItem(row, col, item)

        self._table.resizeColumnsToContents()

    def _clear_flash(self) -> None:
        self._flash_addresses.clear()
        self._flash_timer.stop()
        self._refresh_table()

    def _show_context_menu(self, pos) -> None:
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        addr_text = self._table.item(row, 0).text()
        addr = int(addr_text, 16)
        menu = QMenu(self)
        copy_act = menu.addAction("Copy Row")
        write_act = menu.addAction("Write Value...")
        chart_act = menu.addAction("Add to Trend Chart")
        note_act = menu.addAction("Add Note")
        action = menu.exec(self._table.viewport().mapToGlobal(pos))
        if action == copy_act:
            self._copy_row(row)
        elif action == write_act:
            self._prompt_write(addr)
        elif action == chart_act:
            self.add_to_chart_requested.emit(addr)
        elif action == note_act:
            self._add_note(addr)

    def _header_context_menu(self, pos) -> None:
        menu = QMenu(self)
        for i, name in enumerate(self.COLUMNS):
            act = menu.addAction(name)
            act.setCheckable(True)
            act.setChecked(not self._table.isColumnHidden(i))
            act.setData(i)
        chosen = menu.exec(self._table.horizontalHeader().mapToGlobal(pos))
        if chosen:
            col = chosen.data()
            self._table.setColumnHidden(col, not self._table.isColumnHidden(col))

    def _copy_row(self, row: int) -> None:
        cols = [self._table.item(row, c).text() for c in range(self._table.columnCount())]
        QApplication.clipboard().setText("\t".join(cols))

    def _prompt_write(self, address: int) -> None:
        val, ok = QInputDialog.getInt(self, "Write Register", f"Value for address 0x{address:04X}:", 0, 0, 65535)
        if ok:
            self.write_requested.emit(address, val)

    def _add_note(self, address: int) -> None:
        note, ok = QInputDialog.getText(self, "Add Note", f"Note for address 0x{address:04X}:")
        if ok and note:
            pass

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
        self._flash_addresses.clear()
        self._flash_timer.stop()
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
