import random
from collections import deque

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QPushButton, QSpinBox, QLineEdit, QLabel, QCheckBox,
    QGridLayout, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Signal, QTimer


class PLCTestingPanel(QWidget):
    write_register_requested = Signal(int, int)
    write_coil_requested = Signal(int, bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._stress_timer = QTimer(self)
        self._stress_timer.timeout.connect(self._stress_step)
        self._stress_count = 0
        self._write_history: deque = deque(maxlen=50)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        force_group = QGroupBox("Force / Write")
        fl = QFormLayout(force_group)

        addr_row = QHBoxLayout()
        self._force_addr = QSpinBox()
        self._force_addr.setRange(0, 65535)
        addr_row.addWidget(QLabel("Address:"))
        addr_row.addWidget(self._force_addr)
        fl.addRow(addr_row)

        self._coil_btn = QPushButton("Toggle Coil (FC05)")
        self._coil_btn.clicked.connect(self._toggle_coil)
        fl.addRow(self._coil_btn)

        val_row = QHBoxLayout()
        self._write_val = QSpinBox()
        self._write_val.setRange(0, 65535)
        val_row.addWidget(QLabel("Value:"))
        val_row.addWidget(self._write_val)
        self._write_btn = QPushButton("Write Register (FC06)")
        self._write_btn.clicked.connect(lambda: self._emit_write(
            self._force_addr.value(), self._write_val.value()))
        val_row.addWidget(self._write_btn)
        fl.addRow(val_row)

        undo_btn = QPushButton("Undo Last Write")
        undo_btn.clicked.connect(self._undo_last_write)
        fl.addRow(undo_btn)

        layout.addWidget(force_group)

        inc_group = QGroupBox("Increment / Generate")
        inc_grid = QGridLayout(inc_group)
        self._inc_addr = QSpinBox()
        self._inc_addr.setRange(0, 65535)
        inc_grid.addWidget(QLabel("Start Addr:"), 0, 0)
        inc_grid.addWidget(self._inc_addr, 0, 1)
        self._inc_count = QSpinBox()
        self._inc_count.setRange(1, 100)
        self._inc_count.setValue(10)
        inc_grid.addWidget(QLabel("Count:"), 1, 0)
        inc_grid.addWidget(self._inc_count, 1, 1)
        increment_btn = QPushButton("Increment Values")
        increment_btn.clicked.connect(self._increment_values)
        inc_grid.addWidget(increment_btn, 2, 0, 1, 2)
        random_btn = QPushButton("Random Generator")
        random_btn.clicked.connect(self._random_generator)
        inc_grid.addWidget(random_btn, 3, 0, 1, 2)
        layout.addWidget(inc_group)

        bulk_group = QGroupBox("Bulk Write")
        bulk_layout = QVBoxLayout(bulk_group)
        self._bulk_table = QTableWidget(5, 3)
        self._bulk_table.setHorizontalHeaderLabels(["Address", "Value", "FC"])
        self._bulk_table.horizontalHeader().setStretchLastSection(True)
        bulk_execute_btn = QPushButton("Execute All Writes")
        bulk_execute_btn.clicked.connect(self._bulk_write)
        bulk_layout.addWidget(self._bulk_table)
        bulk_layout.addWidget(bulk_execute_btn)
        layout.addWidget(bulk_group)

        stress_group = QGroupBox("Stress Test")
        stress_fl = QFormLayout(stress_group)
        self._stress_count_spin = QSpinBox()
        self._stress_count_spin.setRange(1, 10000)
        self._stress_count_spin.setValue(100)
        stress_fl.addRow("Iterations:", self._stress_count_spin)
        self._stress_interval = QSpinBox()
        self._stress_interval.setRange(10, 5000)
        self._stress_interval.setValue(100)
        self._stress_interval.setSuffix(" ms")
        stress_fl.addRow("Interval:", self._stress_interval)
        stress_btn_row = QHBoxLayout()
        self._stress_start_btn = QPushButton("Start Stress Test")
        self._stress_start_btn.clicked.connect(self._start_stress)
        stress_btn_row.addWidget(self._stress_start_btn)
        self._stress_stop_btn = QPushButton("Stop")
        self._stress_stop_btn.setEnabled(False)
        self._stress_stop_btn.clicked.connect(self._stop_stress)
        stress_btn_row.addWidget(self._stress_stop_btn)
        stress_fl.addRow(stress_btn_row)
        layout.addWidget(stress_group)

        self._status_output = QTextEdit()
        self._status_output.setReadOnly(True)
        self._status_output.setMaximumHeight(100)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self._status_output)

        layout.addStretch()

    def _emit_write(self, address: int, value: int) -> None:
        self._write_history.append((address, value))
        self.write_register_requested.emit(address, value)
        self._log(f"Write: addr=0x{address:04X} val={value} (0x{value:04X})")

    def _undo_last_write(self) -> None:
        if self._write_history:
            addr, val = self._write_history.pop()
            self._log(f"Undo: re-writing addr=0x{addr:04X} -> 0")
            self.write_register_requested.emit(addr, 0)
        else:
            self._log("No writes to undo")

    def _toggle_coil(self) -> None:
        addr = self._force_addr.value()
        self.write_coil_requested.emit(addr, True)
        self._log(f"Toggled coil at 0x{addr:04X}")

    def _increment_values(self) -> None:
        start = self._inc_addr.value()
        count = self._inc_count.value()
        for i in range(count):
            self._emit_write(start + i, i)
        self._log(f"Incremented {count} registers from 0x{start:04X}")

    def _random_generator(self) -> None:
        start = self._inc_addr.value()
        count = self._inc_count.value()
        for i in range(count):
            self._emit_write(start + i, random.randint(0, 65535))
        self._log(f"Random values written to {count} registers from 0x{start:04X}")

    def _bulk_write(self) -> None:
        count = 0
        for row in range(self._bulk_table.rowCount()):
            addr_item = self._bulk_table.item(row, 0)
            val_item = self._bulk_table.item(row, 1)
            if addr_item and val_item and addr_item.text() and val_item.text():
                try:
                    addr = int(addr_item.text(), 0)
                    val = int(val_item.text(), 0)
                    self._emit_write(addr, val)
                    count += 1
                except ValueError:
                    self._log(f"Row {row + 1}: invalid entry - skipped")
        if count:
            self._log(f"Bulk write: {count} registers written")

    def _start_stress(self) -> None:
        self._stress_count = 0
        self._stress_start_btn.setEnabled(False)
        self._stress_stop_btn.setEnabled(True)
        self._stress_timer.start(self._stress_interval.value())
        self._log("Stress test started")

    def _stress_step(self) -> None:
        self._stress_count += 1
        addr = random.randint(0, 100)
        val = random.randint(0, 65535)
        self._emit_write(addr, val)
        if self._stress_count >= self._stress_count_spin.value():
            self._stop_stress()
            self._log(f"Stress test completed: {self._stress_count} writes")

    def _stop_stress(self) -> None:
        self._stress_timer.stop()
        self._stress_start_btn.setEnabled(True)
        self._stress_stop_btn.setEnabled(False)
        self._log(f"Stress test stopped at {self._stress_count} writes")

    def _log(self, msg: str) -> None:
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self._status_output.append(f"[{ts}] {msg}")
