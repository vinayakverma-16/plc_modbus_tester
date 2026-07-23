import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QPushButton, QSpinBox, QLineEdit, QLabel, QCheckBox,
    QGridLayout, QTextEdit,
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
        self._write_btn.clicked.connect(lambda: self.write_register_requested.emit(
            self._force_addr.value(), self._write_val.value()))
        val_row.addWidget(self._write_btn)
        fl.addRow(val_row)

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

    def _toggle_coil(self) -> None:
        addr = self._force_addr.value()
        self.write_coil_requested.emit(addr, True)
        self._log(f"Toggled coil at {addr}")

    def _increment_values(self) -> None:
        start = self._inc_addr.value()
        count = self._inc_count.value()
        for i in range(count):
            self.write_register_requested.emit(start + i, i)
        self._log(f"Incremented {count} registers from {start}")

    def _random_generator(self) -> None:
        start = self._inc_addr.value()
        count = self._inc_count.value()
        for i in range(count):
            self.write_register_requested.emit(start + i, random.randint(0, 65535))
        self._log(f"Random values written to {count} registers from {start}")

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
        self.write_register_requested.emit(addr, val)
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
