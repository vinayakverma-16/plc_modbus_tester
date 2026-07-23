from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QAbstractItemView, QLabel, QFileDialog,
    QCheckBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from modbus.models import PacketRecord


class PacketMonitor(QWidget):
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

        self._table = QTableWidget()
        self._table.setColumnCount(len(self.COLUMNS))
        self._table.setHorizontalHeaderLabels(self.COLUMNS)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table)

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
