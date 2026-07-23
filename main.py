import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("PLC Test Utility")
    app.setOrganizationName("PLCTestUtility")
    app.setApplicationVersion("1.0.0")

    style_path = os.path.join(os.path.dirname(__file__), "assets", "dark.qss")
    if os.path.exists(style_path):
        with open(style_path, encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
