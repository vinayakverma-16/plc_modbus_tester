from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QPushButton, QComboBox, QTextEdit, QLabel, QFileDialog,
    QCheckBox, QSpinBox,
)


class LoggingPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        config_group = QGroupBox("Log Configuration")
        fl = QFormLayout(config_group)

        self._format_combo = QComboBox()
        self._format_combo.addItems(["txt", "csv", "json"])
        fl.addRow("Format:", self._format_combo)

        self._rotate_check = QCheckBox("Auto Rotate")
        self._rotate_check.setChecked(True)
        fl.addRow(self._rotate_check)

        self._max_size_spin = QSpinBox()
        self._max_size_spin.setRange(1, 100)
        self._max_size_spin.setValue(10)
        self._max_size_spin.setSuffix(" MB")
        fl.addRow("Max Size:", self._max_size_spin)

        self._max_files_spin = QSpinBox()
        self._max_files_spin.setRange(1, 20)
        self._max_files_spin.setValue(5)
        fl.addRow("Max Files:", self._max_files_spin)

        layout.addWidget(config_group)

        btn_layout = QHBoxLayout()
        self._start_btn = QPushButton("Start Logging")
        btn_layout.addWidget(self._start_btn)
        self._clear_btn = QPushButton("Clear Logs")
        btn_layout.addWidget(self._clear_btn)
        layout.addLayout(btn_layout)

        self._log_display = QTextEdit()
        self._log_display.setReadOnly(True)
        font = self._log_display.font()
        font.setFamily("Consolas")
        font.setPointSize(9)
        self._log_display.setFont(font)
        layout.addWidget(QLabel("Log Output:"))
        layout.addWidget(self._log_display)

        self._logging = False
        self._log_manager = None

    def _toggle_logging(self) -> None:
        if not self._logging:
            from logger.log_manager import LogManager
            self._log_manager = LogManager()
            self._log_manager.set_format(self._format_combo.currentText())
            fpath = self._log_manager.start_session()
            self._logging = True
            self._start_btn.setText("Stop Logging")
            self._log(f"Logging started: {fpath}")
        else:
            self._logging = False
            self._start_btn.setText("Start Logging")
            self._log("Logging stopped")

    def log(self, entry: dict) -> None:
        if self._logging and self._log_manager:
            self._log_manager.log(entry)
            self._log(f"[{entry.get('type', 'INFO')}] {entry.get('message', '')}")

    def _log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_display.append(f"[{ts}] {msg}")

    def clear_logs(self) -> None:
        if self._log_manager:
            self._log_manager.clear_logs()
        self._log_display.clear()
