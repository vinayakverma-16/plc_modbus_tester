from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QPushButton, QLineEdit, QSpinBox, QTextEdit, QLabel, QListWidget,
    QGridLayout,
)
from PySide6.QtGui import QFont

from utils.network import NetworkUtils


class UtilityPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        ping_group = QGroupBox("Ping PLC")
        ping_layout = QFormLayout(ping_group)
        self._ping_host = QLineEdit("192.168.1.1")
        ping_layout.addRow("Host:", self._ping_host)
        self._ping_count = QSpinBox()
        self._ping_count.setRange(1, 20)
        self._ping_count.setValue(4)
        ping_layout.addRow("Count:", self._ping_count)
        ping_btn = QPushButton("Ping")
        ping_btn.clicked.connect(self._ping)
        ping_layout.addRow(ping_btn)
        layout.addWidget(ping_group)

        port_group = QGroupBox("TCP Port Test")
        port_layout = QFormLayout(port_group)
        self._port_host = QLineEdit("192.168.1.1")
        port_layout.addRow("Host:", self._port_host)
        self._port_num = QSpinBox()
        self._port_num.setRange(1, 65535)
        self._port_num.setValue(502)
        port_layout.addRow("Port:", self._port_num)
        port_btn = QPushButton("Test Port")
        port_btn.clicked.connect(self._test_port)
        port_layout.addRow(port_btn)
        layout.addWidget(port_group)

        scan_group = QGroupBox("Scan")
        scan_layout = QGridLayout(scan_group)
        serial_btn = QPushButton("Scan Serial Ports")
        serial_btn.clicked.connect(self._scan_serial)
        scan_layout.addWidget(serial_btn, 0, 0)
        net_btn = QPushButton("Scan Network Interfaces")
        net_btn.clicked.connect(self._scan_network)
        scan_layout.addWidget(net_btn, 0, 1)
        layout.addWidget(scan_group)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        font = QFont("Consolas", 10)
        self._output.setFont(font)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self._output)

    def _ping(self) -> None:
        host = self._ping_host.text()
        count = self._ping_count.value()
        result = NetworkUtils.ping(host, count)
        text = (
            f"Ping {host}\n"
            f"Reachable: {result['reachable']}\n"
            f"Avg RTT: {result['avg_ms']:.1f} ms\n"
        )
        self._output.setText(text)

    def _test_port(self) -> None:
        host = self._port_host.text()
        port = self._port_num.value()
        result = NetworkUtils.check_tcp_port(host, port)
        text = (
            f"TCP Port Test: {host}:{port}\n"
            f"Status: {'OPEN' if result['open'] else 'CLOSED'}\n"
        )
        if result["error"]:
            text += f"Error: {result['error']}\n"
        self._output.setText(text)

    def _scan_serial(self) -> None:
        ports = NetworkUtils.scan_serial_ports()
        if not ports:
            self._output.setText("No serial ports found.")
            return
        lines = ["Serial Ports:"]
        for p in ports:
            lines.append(f"  {p['device']} - {p['description']}")
        self._output.setText("\n".join(lines))

    def _scan_network(self) -> None:
        interfaces = NetworkUtils.get_network_interfaces()
        if not interfaces:
            self._output.setText("No network interfaces found.")
            return
        lines = ["Network Interfaces:"]
        for iface in interfaces:
            lines.append(f"  {iface['name']}: {iface['ip']} ({iface['netmask']})")
        self._output.setText("\n".join(lines))
