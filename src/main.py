#!/usr/bin/env python3
"""
SimpleCom - Cross-platform Serial Debug Tool
Main entry point for the application.
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from main_window import MainWindow



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, relative_path)


def main():
    """Application entry point."""
    # High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("SimpleCom")
    app.setOrganizationName("SimpleCom")
    app.setApplicationVersion("1.0.0")

    # Set application icon
    icon_path = resource_path("assets/icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Apply global stylesheet for modern look
    app.setStyleSheet("""
        QMainWindow {
            background-color: #313244;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #45475a;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 10px;
            background-color: #313244;
            color: #cdd6f4;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            color: #89b4fa;
        }
        QLabel {
            color: #cdd6f4;
        }
        QComboBox {
            background-color: #45475a;
            color: #cdd6f4;
            border: 1px solid #585b70;
            border-radius: 4px;
            padding: 5px 10px;
            min-height: 20px;
        }
        QComboBox:hover {
            border-color: #89b4fa;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #cdd6f4;
            margin-right: 5px;
        }
        QComboBox QAbstractItemView {
            background-color: #45475a;
            color: #cdd6f4;
            selection-background-color: #89b4fa;
            selection-color: #1e1e2e;
        }
        QLineEdit {
            background-color: #45475a;
            color: #cdd6f4;
            border: 1px solid #585b70;
            border-radius: 4px;
            padding: 8px;
        }
        QLineEdit:focus {
            border-color: #89b4fa;
        }
        QTextEdit {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 4px;
            padding: 5px;
        }
        QListWidget {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 4px;
            padding: 5px;
        }
        QListWidget::item {
            padding: 5px;
            border-radius: 3px;
        }
        QListWidget::item:hover {
            background-color: #45475a;
        }
        QListWidget::item:selected {
            background-color: #89b4fa;
            color: #1e1e2e;
        }
        QCheckBox {
            color: #cdd6f4;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #585b70;
            border-radius: 4px;
            background-color: #45475a;
        }
        QCheckBox::indicator:hover {
            border-color: #89b4fa;
        }
        QCheckBox::indicator:checked {
            background-color: #89b4fa;
            border-color: #89b4fa;
        }
        QSpinBox {
            background-color: #45475a;
            color: #cdd6f4;
            border: 1px solid #585b70;
            border-radius: 4px;
            padding: 5px;
        }
        QSpinBox:hover {
            border-color: #89b4fa;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #585b70;
            border: none;
            width: 16px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #89b4fa;
        }
        QPushButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #b4befe;
        }
        QPushButton:pressed {
            background-color: #74c7ec;
        }
        QPushButton:disabled {
            background-color: #585b70;
            color: #6c7086;
        }
        QStatusBar {
            background-color: #1e1e2e;
            color: #a6adc8;
            border-top: 1px solid #45475a;
        }
        QSplitter::handle {
            background-color: #45475a;
            width: 2px;
        }
        QSplitter::handle:hover {
            background-color: #89b4fa;
        }
        QScrollBar:vertical {
            background-color: #313244;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #585b70;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #6c7086;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
        QScrollBar:horizontal {
            background-color: #313244;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: #585b70;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #6c7086;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0;
        }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

