from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QComboBox, QSpinBox, QLineEdit, QCheckBox, QPushButton,
    QScrollArea, QFrame, QInputDialog,
)
from PySide6.QtCore import Signal

from modbus.models import (
    ConnectionSettings, ConnectionType, Parity, ModbusFunction, PollSettings,
)
from utils.profiles import ProfileManager


class ConnectionPanel(QWidget):
    connection_applied = Signal(object)
    poll_settings_changed = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._scan_serial_ports()

    def _build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        profile_bar = QHBoxLayout()
        self._profile_combo = QComboBox()
        self._profile_combo.setPlaceholderText("-- Select Profile --")
        self._refresh_profiles()
        save_profile_btn = QPushButton("Save")
        save_profile_btn.setToolTip("Save current settings as profile")
        save_profile_btn.setFixedWidth(40)
        save_profile_btn.clicked.connect(self._save_profile)
        load_profile_btn = QPushButton("Load")
        load_profile_btn.setToolTip("Load selected profile")
        load_profile_btn.setFixedWidth(40)
        load_profile_btn.clicked.connect(self._load_profile)
        profile_bar.addWidget(QLabel("Profile:"))
        profile_bar.addWidget(self._profile_combo, 1)
        profile_bar.addWidget(save_profile_btn)
        profile_bar.addWidget(load_profile_btn)
        layout.addLayout(profile_bar)

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

        self._com_port_widget = QWidget()
        com_row = QHBoxLayout(self._com_port_widget)
        com_row.setContentsMargins(0, 0, 0, 0)
        self._com_port_combo = QComboBox()
        self._com_port_combo.setMinimumWidth(100)
        refresh_btn = QPushButton("R")
        refresh_btn.setFixedWidth(28)
        refresh_btn.setToolTip("Rescan serial ports")
        refresh_btn.clicked.connect(self._scan_serial_ports)
        com_row.addWidget(self._com_port_combo, 1)
        com_row.addWidget(refresh_btn)
        conn_layout.addRow("COM Port:", self._com_port_widget)
        self._com_port_widget.setVisible(False)

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

        status_row = QHBoxLayout()
        self._conn_status_dot = QLabel("⬤")
        self._conn_status_dot.setStyleSheet("color: #888; font-size: 14px;")
        self._conn_status_label = QLabel("Not connected")
        status_row.addWidget(self._conn_status_dot)
        status_row.addWidget(self._conn_status_label)
        status_row.addStretch()
        conn_layout.addRow(status_row)

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

    def _set_com_visible(self, visible: bool) -> None:
        for i in range(self._com_port_row.count()):
            item = self._com_port_row.itemAt(i)
            if item and item.widget():
                item.widget().setVisible(visible)

    def _on_type_changed(self, text: str) -> None:
        is_serial = text in ("RTU", "ASCII")
        self._set_com_visible(is_serial)
        self._baud_combo.setVisible(is_serial)
        self._parity_combo.setVisible(is_serial)
        self._stop_bits_combo.setVisible(is_serial)
        self._data_bits_spin.setVisible(is_serial)
        is_tcp = text == "TCP"
        self._host_input.setVisible(is_tcp)
        self._port_spin.setVisible(is_tcp)

    def _scan_serial_ports(self) -> None:
        self._com_port_combo.clear()
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            if ports:
                for p in ports:
                    self._com_port_combo.addItem(f"{p.device} - {p.description}", p.device)
            else:
                self._com_port_combo.addItem("No ports found", "")
                self._com_port_combo.setEnabled(False)
        except Exception:
            self._com_port_combo.addItem("Scan failed", "")
        self._com_port_combo.setEnabled(self._com_port_combo.count() > 0)

    def _refresh_profiles(self) -> None:
        self._profile_combo.clear()
        mgr = ProfileManager()
        for name in mgr.list_profiles():
            self._profile_combo.addItem(name)

    def _save_profile(self) -> None:
        name, ok = QInputDialog.getText(self, "Save Profile", "Profile name:")
        if ok and name:
            mgr = ProfileManager()
            mgr.save(name, self.get_connection_settings())
            self._refresh_profiles()

    def _load_profile(self) -> None:
        name = self._profile_combo.currentText()
        if name and not name.startswith("--"):
            mgr = ProfileManager()
            try:
                conn = mgr.load(name)
                self.set_connection_settings(conn)
            except Exception:
                pass

    def set_connection_state(self, connected: bool, msg: str = "") -> None:
        if connected:
            self._conn_status_dot.setStyleSheet("color: #4CAF50; font-size: 14px;")
            self._conn_status_label.setText(f"Connected - {msg}" if msg else "Connected")
        else:
            self._conn_status_dot.setStyleSheet("color: #e53935; font-size: 14px;")
            self._conn_status_label.setText("Disconnected")

    def get_connection_settings(self) -> ConnectionSettings:
        settings = ConnectionSettings()
        ctype = self._type_combo.currentText()
        settings.connection_type = ConnectionType(ctype)
        settings.host = self._host_input.text()
        settings.port = self._port_spin.value()
        com_data = self._com_port_combo.currentData()
        settings.com_port = com_data if com_data else self._com_port_combo.currentText()
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
        idx = self._com_port_combo.findData(settings.com_port)
        if idx >= 0:
            self._com_port_combo.setCurrentIndex(idx)
        else:
            self._com_port_combo.setCurrentText(settings.com_port)
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
