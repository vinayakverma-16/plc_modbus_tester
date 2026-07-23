from PySide6.QtWidgets import (
    QMainWindow, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QStatusBar, QLabel, QMessageBox,
    QToolBar, QPushButton, QFileDialog, QInputDialog, QApplication,
)
from PySide6.QtCore import Qt, Slot, QTimer, QSettings
from PySide6.QtGui import QAction, QKeySequence

from modbus.client import ModbusClient
from modbus.models import ConnectionSettings, PollSettings
from utils.session import SessionManager
from utils.profiles import ProfileManager
from ui.connection_panel import ConnectionPanel
from ui.register_view import RegisterView
from ui.packet_monitor import PacketMonitor
from ui.calculator_panel import CalculatorPanel
from ui.converter_panel import ConverterPanel
from ui.bit_tool_panel import BitToolPanel
from ui.plc_testing_panel import PLCTestingPanel
from ui.logging_panel import LoggingPanel
from ui.utility_panel import UtilityPanel
from ui.trend_chart_panel import TrendChartPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PLC Test Utility")
        self.setMinimumSize(800, 600)
        self.showMaximized()

        self._client = ModbusClient()
        self._session_mgr = SessionManager()
        self._profile_mgr = ProfileManager()
        self._dark_mode = True
        self._is_connected = False
        self._pulse_state = False

        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(800)
        self._pulse_timer.timeout.connect(self._pulse_dot)

        self._build_menu_bar()
        self._build_toolbar()
        self._build_central_area()
        self._build_dock_widgets()
        self._default_state = self.saveState()
        self._build_status_bar()
        self._connect_signals()
        self._apply_theme()

        self._restore_saved_layout()

    def _build_menu_bar(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        save_session_act = QAction("Save Session", self, shortcut=QKeySequence.Save)
        save_session_act.triggered.connect(self._save_session)
        file_menu.addAction(save_session_act)
        load_session_act = QAction("Load Session", self, shortcut=QKeySequence.Open)
        load_session_act.triggered.connect(self._load_session)
        file_menu.addAction(load_session_act)
        file_menu.addSeparator()
        exit_act = QAction("Exit", self, shortcut=QKeySequence.Quit)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        view_menu = menubar.addMenu("&View")
        toolbar_act = QAction("Toggle Toolbar", self, checkable=True)
        toolbar_act.setChecked(True)
        toolbar_act.triggered.connect(lambda v: self._toolbar.setVisible(v))
        view_menu.addAction(toolbar_act)
        view_menu.addSeparator()
        theme_act = QAction("Toggle Dark/Light", self, shortcut="Ctrl+T")
        theme_act.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_act)
        restore_act = QAction("Restore Default Layout", self)
        restore_act.triggered.connect(self._restore_layout)
        view_menu.addAction(restore_act)
        reset_act = QAction("Reset Layout", self)
        reset_act.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_act)

        help_menu = menubar.addMenu("&Help")
        about_act = QAction("About", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    def _build_toolbar(self) -> None:
        self._toolbar = QToolBar("Main")
        self._toolbar.setMovable(True)
        self.addToolBar(self._toolbar)

        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setMinimumWidth(100)
        self._toolbar.addWidget(self._connect_btn)

        self._disconnect_btn = QPushButton("Disconnect")
        self._disconnect_btn.setMinimumWidth(100)
        self._disconnect_btn.setEnabled(False)
        self._toolbar.addWidget(self._disconnect_btn)

        self._toolbar.addSeparator()

        self._poll_btn = QPushButton("Start Poll")
        self._poll_btn.setMinimumWidth(100)
        self._poll_btn.setEnabled(False)
        self._toolbar.addWidget(self._poll_btn)

        self._read_once_btn = QPushButton("Read Once")
        self._read_once_btn.setMinimumWidth(100)
        self._read_once_btn.setEnabled(False)
        self._toolbar.addWidget(self._read_once_btn)

        self._toolbar.addSeparator()

        self._stop_poll_btn = QPushButton("Stop Poll")
        self._stop_poll_btn.setMinimumWidth(100)
        self._stop_poll_btn.setEnabled(False)
        self._toolbar.addWidget(self._stop_poll_btn)

    def _build_central_area(self) -> None:
        self._tab_widget = QTabWidget()
        self._register_view = RegisterView()
        self._tab_widget.addTab(self._register_view, "Register View")
        self._trend_chart = TrendChartPanel()
        self._tab_widget.addTab(self._trend_chart, "Trend Chart")
        self.setCentralWidget(self._tab_widget)

    def _build_dock_widgets(self) -> None:
        dock_flags = QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable

        self._connection_dock = QDockWidget("Connection", self)
        self._connection_panel = ConnectionPanel()
        self._connection_dock.setWidget(self._connection_panel)
        self._connection_dock.setFeatures(dock_flags)
        self._connection_dock.setMinimumWidth(200)
        self.addDockWidget(Qt.LeftDockWidgetArea, self._connection_dock)

        self._packet_dock = QDockWidget("Packet Monitor", self)
        self._packet_monitor = PacketMonitor()
        self._packet_dock.setWidget(self._packet_monitor)
        self._packet_dock.setFeatures(dock_flags)
        self._packet_dock.setMinimumHeight(100)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._packet_dock)

        self._calc_dock = QDockWidget("Calculator", self)
        self._calc_panel = CalculatorPanel()
        self._calc_dock.setWidget(self._calc_panel)
        self._calc_dock.setFeatures(dock_flags)
        self._calc_dock.setMinimumWidth(250)
        self.addDockWidget(Qt.RightDockWidgetArea, self._calc_dock)

        self._tools_dock = QDockWidget("Tools", self)
        self._tools_tabs = QTabWidget()
        self._converter_panel = ConverterPanel()
        self._bit_tool_panel = BitToolPanel()
        self._plc_testing_panel = PLCTestingPanel()
        self._logging_panel = LoggingPanel()
        self._utility_panel = UtilityPanel()
        self._tools_tabs.addTab(self._converter_panel, "Converters")
        self._tools_tabs.addTab(self._bit_tool_panel, "Bit Tool")
        self._tools_tabs.addTab(self._plc_testing_panel, "PLC Test")
        self._tools_tabs.addTab(self._logging_panel, "Logging")
        self._tools_tabs.addTab(self._utility_panel, "Utilities")
        self._tools_dock.setWidget(self._tools_tabs)
        self._tools_dock.setFeatures(dock_flags)
        self.addDockWidget(Qt.RightDockWidgetArea, self._tools_dock)

        self.tabifyDockWidget(self._calc_dock, self._tools_dock)
        self._calc_dock.raise_()

        self.setDockOptions(
            QMainWindow.AllowTabbedDocks |
            QMainWindow.AllowNestedDocks |
            QMainWindow.AnimatedDocks
        )

        self.resizeDocks(
            [self._connection_dock], [230], Qt.Horizontal
        )
        self.resizeDocks(
            [self._calc_dock], [320], Qt.Horizontal
        )
        self.resizeDocks(
            [self._packet_dock], [180], Qt.Vertical
        )

    def _build_status_bar(self) -> None:
        self._status_dot = QLabel("⬤")
        self._status_dot.setStyleSheet("color: #888; font-size: 13px;")
        self._status_label = QLabel("Disconnected")
        self._conn_stats_label = QLabel("TX: 0  RX: 0  Err: 0")
        self._latency_label = QLabel("")
        status_bar = self.statusBar()
        status_bar.addWidget(self._status_dot)
        status_bar.addWidget(self._status_label, 1)
        status_bar.addPermanentWidget(self._latency_label)
        status_bar.addPermanentWidget(self._conn_stats_label)

    def _connect_signals(self) -> None:
        worker = self._client.worker

        self._connect_btn.clicked.connect(self._on_connect)
        self._disconnect_btn.clicked.connect(self._on_disconnect)
        self._poll_btn.clicked.connect(self._on_start_poll)
        self._read_once_btn.clicked.connect(self._on_read_once)
        self._stop_poll_btn.clicked.connect(self._on_stop_poll)

        worker.connection_changed.connect(self._on_connection_changed)
        worker.data_received.connect(self._register_view.update_data)
        worker.data_received.connect(self._trend_chart.update_data)
        worker.packet_logged.connect(self._packet_monitor.add_packet)
        worker.error_occurred.connect(self._on_error)
        worker.stats_updated.connect(self._on_stats_updated)

        self._connection_panel.connection_applied.connect(self._on_connection_applied)
        self._connection_panel.poll_settings_changed.connect(self._on_poll_settings_changed)
        self._plc_testing_panel.write_register_requested.connect(self._on_write_register)
        self._plc_testing_panel.write_coil_requested.connect(self._on_write_coil)
        self._register_view.add_to_chart_requested.connect(self._on_add_to_chart)

    def _on_add_to_chart(self, address: int) -> None:
        self._trend_chart.add_register(address)
        self._tab_widget.setCurrentIndex(1)

    def _apply_theme(self) -> None:
        import os
        theme_file = "dark.qss" if self._dark_mode else "light.qss"
        style_path = os.path.join(os.path.dirname(__file__), "..", "assets", theme_file)
        if os.path.exists(style_path):
            with open(style_path, encoding="utf-8") as f:
                qApp = QApplication.instance()
                if qApp:
                    qApp.setStyleSheet(f.read())

    def _restore_saved_layout(self) -> None:
        settings = QSettings("PLCTestUtility", "MainWindow")
        geo = settings.value("geometry")
        state = settings.value("windowState")
        if geo:
            self.restoreGeometry(geo)
        if state:
            self.restoreState(state)

    def _restore_layout(self) -> None:
        self.restoreState(self._default_state)

    def _reset_layout(self) -> None:
        QSettings("PLCTestUtility", "MainWindow").clear()
        QMessageBox.information(self, "Layout Reset", "Layout will reset on next restart.")

    def _pulse_dot(self) -> None:
        if not self._is_connected:
            return
        self._pulse_state = not self._pulse_state
        color = "#4CAF50" if self._pulse_state else "#2e7d32"
        self._status_dot.setStyleSheet(f"color: {color}; font-size: 13px;")

    @Slot()
    def _toggle_theme(self) -> None:
        self._dark_mode = not self._dark_mode
        self._apply_theme()

    @Slot()
    def _on_connect(self) -> None:
        settings = self._connection_panel.get_connection_settings()
        self._client.connect(settings)

    @Slot()
    def _on_disconnect(self) -> None:
        self._client.disconnect()
        self._on_connection_changed(False, "Disconnected")

    @Slot()
    def _on_start_poll(self) -> None:
        poll_settings = self._connection_panel.get_poll_settings()
        self._client.start_polling(poll_settings)
        self._poll_btn.setEnabled(False)
        self._stop_poll_btn.setEnabled(True)
        self._read_once_btn.setEnabled(False)

    @Slot()
    def _on_read_once(self) -> None:
        poll_settings = self._connection_panel.get_poll_settings()
        self._client.worker._poll_settings = poll_settings
        registers = self._client.read_once()
        if registers:
            self._register_view.update_data(registers)

    @Slot()
    def _on_stop_poll(self) -> None:
        self._client.stop_polling()
        self._poll_btn.setEnabled(True)
        self._stop_poll_btn.setEnabled(False)
        self._read_once_btn.setEnabled(True)

    @Slot(bool, str)
    def _on_connection_changed(self, connected: bool, msg: str) -> None:
        self._connection_panel.set_connection_state(connected, msg)
        if connected:
            self._is_connected = True
            self._status_label.setText(f"Connected - {msg}")
            self._status_dot.setStyleSheet("color: #4CAF50; font-size: 13px;")
            self._pulse_timer.start()
            self._connect_btn.setEnabled(False)
            self._disconnect_btn.setEnabled(True)
            self._poll_btn.setEnabled(True)
            self._read_once_btn.setEnabled(True)
        else:
            self._is_connected = False
            self._pulse_timer.stop()
            self._status_label.setText(f"Disconnected - {msg}")
            self._status_dot.setStyleSheet("color: #e53935; font-size: 13px;")
            self._connect_btn.setEnabled(True)
            self._disconnect_btn.setEnabled(False)
            self._poll_btn.setEnabled(False)
            self._read_once_btn.setEnabled(False)
            self._stop_poll_btn.setEnabled(False)
            self._on_stop_poll()

    @Slot(str)
    def _on_error(self, msg: str) -> None:
        self._packet_monitor.log_error(msg)

    @Slot(object)
    def _on_stats_updated(self, stats) -> None:
        self._conn_stats_label.setText(
            f"TX: {stats.packets_sent}  RX: {stats.packets_received}  Err: {stats.errors}"
        )
        if hasattr(stats, 'latency_ms') and stats.latency_ms > 0:
            self._latency_label.setText(f"RTT: {stats.latency_ms:.1f}ms")

    @Slot(object)
    def _on_connection_applied(self, settings: ConnectionSettings) -> None:
        self._connection_panel.set_connection_settings(settings)

    @Slot(object)
    def _on_poll_settings_changed(self, settings: PollSettings) -> None:
        pass

    @Slot(int, int)
    def _on_write_register(self, address: int, value: int) -> None:
        settings = self._connection_panel.get_connection_settings()
        self._client.write_register(address, value, settings.slave_id)

    @Slot(int, bool)
    def _on_write_coil(self, address: int, value: bool) -> None:
        settings = self._connection_panel.get_connection_settings()
        self._client.write_coil(address, value, settings.slave_id)

    @Slot()
    def _save_session(self) -> None:
        name, ok = QInputDialog.getText(self, "Save Session", "Session name:")
        if ok and name:
            conn = self._connection_panel.get_connection_settings()
            poll = self._connection_panel.get_poll_settings()
            self._session_mgr.save(name, conn, poll)
            self._status_label.setText(f"Session '{name}' saved")

    @Slot()
    def _load_session(self) -> None:
        sessions = self._session_mgr.list_sessions()
        if not sessions:
            QMessageBox.information(self, "Load Session", "No saved sessions found.")
            return
        name, ok = QInputDialog.getItem(self, "Load Session", "Select session:", sessions, 0, False)
        if ok and name:
            try:
                conn, poll = self._session_mgr.load(name)
                self._connection_panel.set_connection_settings(conn)
                self._connection_panel.set_poll_settings(poll)
                self._status_label.setText(f"Session '{name}' loaded")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    @Slot()
    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About PLC Test Utility",
            "PLC Test Utility v1.0.0\n\n"
            "A professional Modbus communication and PLC testing tool.\n\n"
            "Built with Python, PySide6, and pymodbus.\n\n"
            "Open source under MIT License."
        )

    def closeEvent(self, event) -> None:
        settings = QSettings("PLCTestUtility", "MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        self._client.cleanup()
        super().closeEvent(event)
