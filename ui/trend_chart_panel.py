from collections import deque

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Slot
import pyqtgraph as pg


MAX_POINTS = 200


class TrendChartPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._traces: dict[int, dict] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        toolbar = QHBoxLayout()
        self._clear_btn = QPushButton("Clear All")
        self._clear_btn.clicked.connect(self._clear_traces)
        toolbar.addWidget(self._clear_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        pg.setConfigOption("background", "#1e1e2e")
        pg.setConfigOption("foreground", "#cdd6f4")
        self._plot = pg.PlotWidget()
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.setLabel("left", "Value")
        self._plot.setLabel("bottom", "Samples")
        self._plot.addLegend()
        layout.addWidget(self._plot)

    COLORS = ["#89b4fa", "#a6e3a1", "#fab387", "#f38ba8", "#cba6f7", "#94e2d5"]

    def add_register(self, address: int) -> None:
        if address in self._traces:
            return
        color = self.COLORS[len(self._traces) % len(self.COLORS)]
        data = deque([0] * MAX_POINTS, maxlen=MAX_POINTS)
        curve = self._plot.plot(list(data), name=f"0x{address:04X}", pen=pg.mkPen(color, width=2))
        self._traces[address] = {"data": data, "curve": curve}

    @Slot(list)
    def update_data(self, registers: list) -> None:
        for reg in registers:
            if reg.address in self._traces:
                trace = self._traces[reg.address]
                trace["data"].append(reg.value)
                trace["curve"].setData(list(trace["data"]))

    def _clear_traces(self) -> None:
        for trace in self._traces.values():
            self._plot.removeItem(trace["curve"])
        self._traces.clear()
