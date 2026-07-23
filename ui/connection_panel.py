from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QComboBox, QSpinBox, QLineEdit, QCheckBox, QPushButton,
    QScrollArea, QFrame,
)
from PySide6.QtCore import Signal

from modbus.models import (
    ConnectionSettings, ConnectionType, Parity, ModbusFunction, PollSettings,
)


class ConnectionPanel(QWidget):
    connection_applied = Signal(object)
    poll_settings_changed = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        conn_group = QGroupBox("Connection")
        conn_layout = QFormLayout(conn_group)

        self._type_combo = QComboBox()
        self._type_combo.addItems(["TCP", "RTU", "ASCII"])
        self._type_combo.currentTextChanged.connect(self._on_type_changed)
        conn_layout.addRow("Type:", self._type_combo)

        self._host_input = QLineEdit("127.0.0.1")
        conn_layout.addRow("Host:", self._host_input)

        self._port_spin = QSpinBox()
        self._port_spin.setRange(1, 65535)
        self._port_spin.setValue(502)
        conn_layout.addRow("Port:", self._port_spin)

        self._com_port_input = QLineEdit("COM1")
        self._com_port_input.setVisible(False)
        conn_layout.addRow("COM Port:", self._com_port_input)

        self._baud_combo = QComboBox()
        self._baud_combo.addItems(["1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"])
        self._baud_combo.setCurrentText("9600")
        self._baud_combo.setVisible(False)
        conn_layout.addRow("Baud Rate:", self._baud_combo)

        self._parity_combo = QComboBox()
        self._parity_combo.addItems(["None", "Even", "Odd"])
        self._parity_combo.setVisible(False)
        conn_layout.addRow("Parity:", self._parity_combo)

        self._stop_bits_combo = QComboBox()
        self._stop_bits_combo.addItems(["1", "1.5", "2"])
        self._stop_bits_combo.setVisible(False)
        conn_layout.addRow("Stop Bits:", self._stop_bits_combo)

        self._data_bits_spin = QSpinBox()
        self._data_bits_spin.setRange(5, 8)
        self._data_bits_spin.setValue(8)
        self._data_bits_spin.setVisible(False)
        conn_layout.addRow("Data Bits:", self._data_bits_spin)

        self._timeout_spin = QSpinBox()
        self._timeout_spin.setRange(1, 60)
        self._timeout_spin.setValue(3)
        self._timeout_spin.setSuffix(" s")
        conn_layout.addRow("Timeout:", self._timeout_spin)

        self._slave_id_spin = QSpinBox()
        self._slave_id_spin.setRange(1, 247)
        self._slave_id_spin.setValue(1)
        conn_layout.addRow("Slave ID:", self._slave_id_spin)

        self._auto_reconnect_check = QCheckBox("Auto Reconnect")
        conn_layout.addRow(self._auto_reconnect_check)

        self._retry_spin = QSpinBox()
        self._retry_spin.setRange(0, 10)
        self._retry_spin.setValue(3)
        conn_layout.addRow("Retry Count:", self._retry_spin)

        layout.addWidget(conn_group)

        poll_group = QGroupBox("Poll Settings")
        poll_layout = QFormLayout(poll_group)

        self._fc_combo = QComboBox()
        for fc in ModbusFunction:
            self._fc_combo.addItem(f"FC{fc.value:02d} {fc.name.replace('_', ' ').title()}", fc.value)
        poll_layout.addRow("Function:", self._fc_combo)

        self._start_addr_spin = QSpinBox()
        self._start_addr_spin.setRange(0, 65535)
        poll_layout.addRow("Start Addr:", self._start_addr_spin)

        self._quantity_spin = QSpinBox()
        self._quantity_spin.setRange(1, 125)
        self._quantity_spin.setValue(10)
        poll_layout.addRow("Quantity:", self._quantity_spin)

        self._interval_spin = QSpinBox()
        self._interval_spin.setRange(10, 60000)
        self._interval_spin.setValue(1000)
        self._interval_spin.setSuffix(" ms")
        poll_layout.addRow("Interval:", self._interval_spin)

        self._continuous_check = QCheckBox("Continuous Poll")
        self._continuous_check.setChecked(True)
        poll_layout.addRow(self._continuous_check)

        layout.addWidget(poll_group)

        layout.addStretch()
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _on_type_changed(self, text: str) -> None:
        is_serial = text in ("RTU", "ASCII")
        self._com_port_input.setVisible(is_serial)
        self._baud_combo.setVisible(is_serial)
        self._parity_combo.setVisible(is_serial)
        self._stop_bits_combo.setVisible(is_serial)
        self._data_bits_spin.setVisible(is_serial)
        is_tcp = text == "TCP"
        self._host_input.setVisible(is_tcp)
        self._port_spin.setVisible(is_tcp)

    def get_connection_settings(self) -> ConnectionSettings:
        settings = ConnectionSettings()
        ctype = self._type_combo.currentText()
        settings.connection_type = ConnectionType(ctype)
        settings.host = self._host_input.text()
        settings.port = self._port_spin.value()
        settings.com_port = self._com_port_input.text()
        settings.baud_rate = int(self._baud_combo.currentText())
        parity_map = {"None": Parity.NONE, "Even": Parity.EVEN, "Odd": Parity.ODD}
        settings.parity = parity_map[self._parity_combo.currentText()]
        stop_map = {"1": 1, "1.5": 1.5, "2": 2}
        settings.stop_bits = stop_map[self._stop_bits_combo.currentText()]
        settings.data_bits = self._data_bits_spin.value()
        settings.timeout = self._timeout_spin.value()
        settings.slave_id = self._slave_id_spin.value()
        settings.auto_reconnect = self._auto_reconnect_check.isChecked()
        settings.retry_count = self._retry_spin.value()
        return settings

    def get_poll_settings(self) -> PollSettings:
        settings = PollSettings()
        fc_val = self._fc_combo.currentData()
        settings.function_code = ModbusFunction(fc_val)
        settings.start_address = self._start_addr_spin.value()
        settings.quantity = self._quantity_spin.value()
        settings.poll_interval_ms = self._interval_spin.value()
        settings.continuous = self._continuous_check.isChecked()
        return settings

    def set_connection_settings(self, settings: ConnectionSettings) -> None:
        self._type_combo.setCurrentText(settings.connection_type.value)
        self._host_input.setText(settings.host)
        self._port_spin.setValue(settings.port)
        self._com_port_input.setText(settings.com_port)
        self._baud_combo.setCurrentText(str(settings.baud_rate))
        parity_map = {Parity.NONE: "None", Parity.EVEN: "Even", Parity.ODD: "Odd"}
        self._parity_combo.setCurrentText(parity_map[settings.parity])
        stop_map = {1: "1", 1.5: "1.5", 2: "2"}
        self._stop_bits_combo.setCurrentText(stop_map[settings.stop_bits])
        self._data_bits_spin.setValue(settings.data_bits)
        self._timeout_spin.setValue(settings.timeout)
        self._slave_id_spin.setValue(settings.slave_id)
        self._auto_reconnect_check.setChecked(settings.auto_reconnect)
        self._retry_spin.setValue(settings.retry_count)

    def set_poll_settings(self, settings: PollSettings) -> None:
        idx = self._fc_combo.findData(settings.function_code.value)
        if idx >= 0:
            self._fc_combo.setCurrentIndex(idx)
        self._start_addr_spin.setValue(settings.start_address)
        self._quantity_spin.setValue(settings.quantity)
        self._interval_spin.setValue(settings.poll_interval_ms)
        self._continuous_check.setChecked(settings.continuous)
