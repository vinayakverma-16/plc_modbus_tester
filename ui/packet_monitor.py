from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QAbstractItemView, QLabel, QFileDialog,
    QCheckBox, QLineEdit, QComboBox, QTextEdit, QMenu, QApplication,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from modbus.models import PacketRecord


class PacketMonitor(QWidget):
    resend_requested = Signal(str)

    COLUMNS = ["Time", "Dir", "Hex Data", "ASCII", "CRC", "Length", "Error"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._packets: list[PacketRecord] = []
        self._max_packets = 1000
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        toolbar = QHBoxLayout()
        self._pause_check = QCheckBox("Pause")
        toolbar.addWidget(self._pause_check)
        toolbar.addStretch()
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.clicked.connect(self.clear)
        toolbar.addWidget(self._clear_btn)
        self._save_btn = QPushButton("Save")
        self._save_btn.clicked.connect(self._save_log)
        toolbar.addWidget(self._save_btn)
        layout.addLayout(toolbar)

        filter_bar = QHBoxLayout()
        self._filter_input = QLineEdit()
        self._filter_input.setPlaceholderText("Filter (hex, ASCII, error)...")
        self._filter_input.textChanged.connect(self._apply_filter)
        self._dir_filter = QComboBox()
        self._dir_filter.addItems(["All", "TX", "RX", "ERR"])
        self._dir_filter.currentTextChanged.connect(self._apply_filter)
        self._autoscroll_check = QCheckBox("Auto-scroll")
        self._autoscroll_check.setChecked(True)
        filter_bar.addWidget(QLabel("Filter:"))
        filter_bar.addWidget(self._filter_input, 1)
        filter_bar.addWidget(self._dir_filter)
        filter_bar.addWidget(self._autoscroll_check)
        layout.addLayout(filter_bar)

        self._table = QTableWidget()
        self._table.setColumnCount(len(self.COLUMNS))
        self._table.setHorizontalHeaderLabels(self.COLUMNS)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._packet_context_menu)
        self._table.clicked.connect(self._decode_packet)
        layout.addWidget(self._table)

        self._decode_view = QTextEdit()
        self._decode_view.setReadOnly(True)
        self._decode_view.setMaximumHeight(80)
        self._decode_view.setFont(QFont("Consolas", 9))
        self._decode_view.setPlaceholderText("Click a packet row to decode...")
        layout.addWidget(QLabel("Decoded:"))
        layout.addWidget(self._decode_view)

        self._tx_color = QColor(100, 150, 255, 60)
        self._rx_color = QColor(100, 255, 100, 60)
        self._err_color = QColor(255, 100, 100, 60)

    def add_packet(self, packet: PacketRecord) -> None:
        if self._pause_check.isChecked():
            return
        self._packets.append(packet)
        if len(self._packets) > self._max_packets:
            self._packets.pop(0)
        self._refresh()

    def log_error(self, msg: str) -> None:
        packet = PacketRecord(
            timestamp="",
            direction="ERR",
            hex_data="",
            ascii_data="",
            crc="",
            error=msg,
            length=0,
        )
        self.add_packet(packet)

    def _refresh(self) -> None:
        self._table.setRowCount(len(self._packets))
        for row, pkt in enumerate(self._packets):
            items = [
                pkt.timestamp,
                pkt.direction,
                pkt.hex_data,
                pkt.ascii_data,
                pkt.crc,
                str(pkt.length),
                pkt.error,
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                if pkt.direction == "TX":
                    item.setBackground(self._tx_color)
                elif pkt.direction == "RX":
                    item.setBackground(self._rx_color)
                elif pkt.direction == "ERR":
                    item.setBackground(self._err_color)
                self._table.setItem(row, col, item)

        self._apply_filter()

        if self._autoscroll_check.isChecked():
            self._table.scrollToBottom()

    def _apply_filter(self) -> None:
        search = self._filter_input.text().lower()
        dir_f = self._dir_filter.currentText()
        for row in range(self._table.rowCount()):
            pkt = self._packets[row]
            dir_match = dir_f == "All" or pkt.direction == dir_f
            text_match = (not search) or search in pkt.hex_data.lower() or search in pkt.ascii_data.lower() or search in pkt.error.lower()
            self._table.setRowHidden(row, not (dir_match and text_match))

    def _decode_packet(self, index) -> None:
        row = index.row()
        if row >= len(self._packets):
            return
        pkt = self._packets[row]
        parts = pkt.hex_data.strip().split()
        lines = [
            f"Direction : {pkt.direction}",
            f"Timestamp : {pkt.timestamp}",
            f"Length    : {pkt.length} bytes",
            f"Hex Data  : {pkt.hex_data}",
            f"ASCII     : {pkt.ascii_data}",
            f"CRC       : {pkt.crc}",
        ]
        if len(parts) >= 2:
            try:
                lines.append(f"Slave ID  : {int(parts[0], 16)}")
                lines.append(f"Func Code : FC{int(parts[1], 16):02d}")
            except ValueError:
                pass
        if pkt.error:
            lines.append(f"Error     : {pkt.error}")
        self._decode_view.setText("\n".join(lines))

    def _packet_context_menu(self, pos) -> None:
        row = self._table.rowAt(pos.y())
        if row < 0 or row >= len(self._packets):
            return
        pkt = self._packets[row]
        menu = QMenu(self)
        copy_hex = menu.addAction("Copy Hex Data")
        resend = menu.addAction("Resend TX Packet")
        resend.setEnabled(pkt.direction == "TX")
        action = menu.exec(self._table.viewport().mapToGlobal(pos))
        if action == copy_hex:
            QApplication.clipboard().setText(pkt.hex_data)
        elif action == resend:
            self.resend_requested.emit(pkt.hex_data)

    def clear(self) -> None:
        self._packets.clear()
        self._refresh()

    def _save_log(self) -> None:
        fpath, _ = QFileDialog.getSaveFileName(self, "Save Packet Log", "packets.csv", "CSV (*.csv)")
        if not fpath:
            return
        import csv
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.COLUMNS)
            for pkt in self._packets:
                writer.writerow([
                    pkt.timestamp, pkt.direction, pkt.hex_data,
                    pkt.ascii_data, pkt.crc, pkt.length, pkt.error,
                ])
