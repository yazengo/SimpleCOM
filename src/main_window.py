"""
Main window UI for the serial debug tool.
"""

from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QComboBox, QPushButton,
    QLineEdit, QTextEdit, QListWidget, QSplitter,
    QGroupBox, QStatusBar, QMessageBox, QMenu, QSpinBox
)
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QFont, QKeyEvent, QColor, QPalette, QAction, QShortcut, QKeySequence

from serial_worker import SerialWorker


class MainWindow(QMainWindow):
    """Main application window."""

    BAUDRATES = [
        "115200", "921600"
    ]

    def __init__(self):
        super().__init__()
        self.settings = QSettings("SimpleCom", "SerialDebugTool")
        self.serial_worker = SerialWorker()
        self._need_timestamp = True  # Flag to track if next data needs timestamp
        self._batch_lines = []  # Lines to send in batch mode
        self._batch_index = 0  # Current line index in batch mode
        self._batch_timer = QTimer(self)  # Timer for batch send interval
        self._batch_timer.timeout.connect(self._send_next_batch_line)
        self._setup_ui()
        self._connect_signals()
        self._load_settings()
        self._refresh_ports()

    def _setup_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("SimpleCom - Serial Debug Tool")
        self.setMinimumSize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Connection settings group
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QGridLayout(connection_group)
        connection_layout.setSpacing(8)

        # Port selection
        port_label = QLabel("Port:")
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedWidth(80)

        # Baudrate selection
        baudrate_label = QLabel("Baudrate:")
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(self.BAUDRATES)
        self.baudrate_combo.setCurrentText("115200")
        self.baudrate_combo.setMinimumWidth(100)

        # Connect/Disconnect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedWidth(100)
        self._update_connect_button(False)

        connection_layout.addWidget(port_label, 0, 0)
        connection_layout.addWidget(self.port_combo, 0, 1)
        connection_layout.addWidget(self.refresh_btn, 0, 2)
        connection_layout.addWidget(baudrate_label, 0, 3)
        connection_layout.addWidget(self.baudrate_combo, 0, 4)
        connection_layout.addWidget(self.connect_btn, 0, 5)
        connection_layout.setColumnStretch(1, 1)

        main_layout.addWidget(connection_group)

        # Create horizontal splitter for left (receive+send) and right (history)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Receive + Send (stacked vertically)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Receive display group
        receive_group = QGroupBox("Received Data")
        receive_layout = QVBoxLayout(receive_group)

        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)
        self.receive_text.setFont(QFont("Consolas", 10))
        self._apply_terminal_style(self.receive_text)

        # Clear button for receive area
        clear_btn_layout = QHBoxLayout()
        clear_btn_layout.addStretch()
        self.clear_receive_btn = QPushButton("Clear")
        self.clear_receive_btn.setFixedWidth(80)
        clear_btn_layout.addWidget(self.clear_receive_btn)

        receive_layout.addWidget(self.receive_text)
        receive_layout.addLayout(clear_btn_layout)

        left_layout.addWidget(receive_group, 1)

        # Send group (combined single line and batch send)
        send_group = QGroupBox("Send Data")
        send_main_layout = QVBoxLayout(send_group)

        # Batch text input (multi-line)
        self.batch_text = QTextEdit()
        self.batch_text.setFont(QFont("Consolas", 10))
        self.batch_text.setPlaceholderText("Enter commands here (one per line for batch send)...")
        self.batch_text.setMaximumHeight(100)
        self._apply_terminal_style(self.batch_text)
        send_main_layout.addWidget(self.batch_text)

        # Controls row
        controls_layout = QHBoxLayout()

        # Line ending option
        controls_layout.addWidget(QLabel("Line Ending:"))
        self.newline_combo = QComboBox()
        self.newline_combo.addItems(["None", "CR", "LF", "CR+LF"])
        self.newline_combo.setCurrentText("CR+LF")
        self.newline_combo.setFixedWidth(80)
        controls_layout.addWidget(self.newline_combo)

        # Interval for batch send
        controls_layout.addWidget(QLabel("Interval (ms):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(0, 10000)
        self.interval_spin.setValue(100)
        self.interval_spin.setSingleStep(50)
        self.interval_spin.setFixedWidth(80)
        controls_layout.addWidget(self.interval_spin)

        controls_layout.addStretch()

        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedWidth(80)
        self.send_btn.setEnabled(False)
        controls_layout.addWidget(self.send_btn)

        # Stop button for batch
        self.batch_stop_btn = QPushButton("Stop")
        self.batch_stop_btn.setFixedWidth(60)
        self.batch_stop_btn.setEnabled(False)
        controls_layout.addWidget(self.batch_stop_btn)

        send_main_layout.addLayout(controls_layout)

        left_layout.addWidget(send_group)

        # Right side: History group (extends to bottom)
        history_group = QGroupBox("Command History")
        history_layout = QVBoxLayout(history_group)

        self.history_list = QListWidget()
        self.history_list.setFont(QFont("Consolas", 10))
        self.history_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Clear history button
        clear_history_layout = QHBoxLayout()
        clear_history_layout.addStretch()
        self.clear_history_btn = QPushButton("Clear")
        self.clear_history_btn.setFixedWidth(80)
        clear_history_layout.addWidget(self.clear_history_btn)

        history_layout.addWidget(self.history_list)
        history_layout.addLayout(clear_history_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(history_group)
        splitter.setSizes([600, 250])

        main_layout.addWidget(splitter, 1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Select a port and click Connect.")

    def _apply_terminal_style(self, text_edit: QTextEdit) -> None:
        """Apply terminal-like dark style to text edit."""
        palette = text_edit.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e2e"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#cdd6f4"))
        text_edit.setPalette(palette)

    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.refresh_btn.clicked.connect(self._refresh_ports)
        self.connect_btn.clicked.connect(self._toggle_connection)
        self.send_btn.clicked.connect(self._start_send)
        self.batch_stop_btn.clicked.connect(self._stop_batch_send)
        self.clear_receive_btn.clicked.connect(self._clear_receive)
        self.clear_history_btn.clicked.connect(self._clear_history)
        self.history_list.itemDoubleClicked.connect(self._history_item_clicked)
        self.history_list.customContextMenuRequested.connect(self._show_history_context_menu)

        # Delete key shortcut for history list
        delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self.history_list)
        delete_shortcut.activated.connect(self._delete_selected_history)

        # Serial worker signals
        self.serial_worker.data_received.connect(self._on_data_received)
        self.serial_worker.error_occurred.connect(self._on_error)
        self.serial_worker.connection_changed.connect(self._on_connection_changed)

    def _refresh_ports(self) -> None:
        """Refresh the list of available serial ports."""
        current_port = self.port_combo.currentData()
        self.port_combo.clear()
        ports = SerialWorker.get_available_ports()

        if ports:
            # Add ports with description as display text and device as data
            for device, description in ports:
                self.port_combo.addItem(description, device)

            # Try to restore previous selection or last saved port
            port_to_select = current_port or getattr(self, '_last_port', '')
            for i in range(self.port_combo.count()):
                if self.port_combo.itemData(i) == port_to_select:
                    self.port_combo.setCurrentIndex(i)
                    break
            self.status_bar.showMessage(f"Found {len(ports)} port(s)")
        else:
            self.status_bar.showMessage("No serial ports found")

    def _toggle_connection(self) -> None:
        """Toggle serial port connection."""
        if self.serial_worker.is_connected():
            self.serial_worker.stop()
        else:
            port = self.port_combo.currentData()
            baudrate = int(self.baudrate_combo.currentText())

            if not port:
                QMessageBox.warning(self, "Error", "Please select a serial port")
                return

            self.serial_worker.configure(port, baudrate)
            if self.serial_worker.connect_port():
                self.serial_worker.start()
                self.status_bar.showMessage(f"Connected to {port} at {baudrate} baud")
            else:
                self.status_bar.showMessage("Connection failed")

    def _update_connect_button(self, connected: bool) -> None:
        """Update connect button appearance based on connection state."""
        if connected:
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet(
                "QPushButton { background-color: #e64553; color: white; "
                "border-radius: 4px; padding: 5px; }"
                "QPushButton:hover { background-color: #d13845; }"
            )
        else:
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet(
                "QPushButton { background-color: #40a02b; color: white; "
                "border-radius: 4px; padding: 5px; }"
                "QPushButton:hover { background-color: #369021; }"
            )

    def _on_connection_changed(self, connected: bool) -> None:
        """Handle connection state change."""
        self._update_connect_button(connected)
        self.send_btn.setEnabled(connected and not self._batch_timer.isActive())
        self.port_combo.setEnabled(not connected)
        self.baudrate_combo.setEnabled(not connected)
        self.refresh_btn.setEnabled(not connected)

        if not connected:
            self._stop_batch_send()  # Stop batch if disconnected
            self.status_bar.showMessage("Disconnected")

    def _start_send(self) -> None:
        """Start sending data (single or batch mode)."""
        text = self.batch_text.toPlainText().strip()
        if not text:
            return

        # Parse lines (skip empty lines)
        self._batch_lines = [line for line in text.split('\n') if line.strip()]
        if not self._batch_lines:
            return

        self._batch_index = 0
        self.send_btn.setEnabled(False)
        self.batch_stop_btn.setEnabled(True)
        self.batch_text.setReadOnly(True)

        # Send first line immediately
        self._send_next_batch_line()

    def _add_to_history(self, text: str) -> None:
        """Add command to history list."""
        # Check if command already exists in history
        for i in range(self.history_list.count()):
            if self.history_list.item(i).text() == text:
                # Move existing item to top
                item = self.history_list.takeItem(i)
                self.history_list.insertItem(0, item)
                return

        # Add new command at top
        self.history_list.insertItem(0, text)

        # Limit history to 100 items
        while self.history_list.count() > 100:
            self.history_list.takeItem(self.history_list.count() - 1)

    def _history_item_clicked(self, item) -> None:
        """Handle history item double-click."""
        self.batch_text.setPlainText(item.text())
        self.batch_text.setFocus()

    def _show_history_context_menu(self, position) -> None:
        """Show context menu for history list."""
        if not self.history_list.selectedItems():
            return

        menu = QMenu(self)
        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self._delete_selected_history)
        menu.addAction(delete_action)

        menu.exec(self.history_list.mapToGlobal(position))

    def _delete_selected_history(self) -> None:
        """Delete selected items from history list."""
        selected_items = self.history_list.selectedItems()
        for item in selected_items:
            row = self.history_list.row(item)
            self.history_list.takeItem(row)

    def _stop_batch_send(self) -> None:
        """Stop batch sending."""
        self._batch_timer.stop()
        self._batch_lines = []
        self._batch_index = 0
        self.send_btn.setEnabled(self.serial_worker.is_connected())
        self.batch_stop_btn.setEnabled(False)
        self.batch_text.setReadOnly(False)
        self.status_bar.showMessage("Send stopped")

    def _send_next_batch_line(self) -> None:
        """Send the next line in batch mode."""
        self._batch_timer.stop()

        if self._batch_index >= len(self._batch_lines):
            # All lines sent
            self._stop_batch_send()
            self.status_bar.showMessage("Send completed")
            return

        if not self.serial_worker.is_connected():
            self._stop_batch_send()
            self.status_bar.showMessage("Send aborted: disconnected")
            return

        # Get current line and send
        line = self._batch_lines[self._batch_index]

        # Add line ending
        line_ending = self.newline_combo.currentText()
        if line_ending == "CR":
            line += "\r"
        elif line_ending == "LF":
            line += "\n"
        elif line_ending == "CR+LF":
            line += "\r\n"

        data = line.encode('utf-8')
        original_line = self._batch_lines[self._batch_index]
        if self.serial_worker.send_data(data):
            self._add_to_history(original_line)
            if len(self._batch_lines) > 1:
                self.status_bar.showMessage(
                    f"Sent [{self._batch_index + 1}/{len(self._batch_lines)}]: {original_line}"
                )
            else:
                self.status_bar.showMessage(f"Sent: {original_line}")

        self._batch_index += 1

        # Schedule next line if more lines remain
        if self._batch_index < len(self._batch_lines):
            interval = self.interval_spin.value()
            if interval > 0:
                self._batch_timer.start(interval)
            else:
                # No delay, send immediately
                self._send_next_batch_line()
        else:
            # All done
            self._stop_batch_send()
            if len(self._batch_lines) > 1:
                self.status_bar.showMessage("All commands sent")

    def _on_data_received(self, data: bytes) -> None:
        """Handle received data from serial port."""
        try:
            text = data.decode('utf-8', errors='replace')
            self.receive_text.moveCursor(
                self.receive_text.textCursor().MoveOperation.End
            )

            # Process text line by line to add timestamps
            result = ""
            for char in text:
                if self._need_timestamp:
                    timestamp = datetime.now().strftime("[%H:%M:%S.%f")[:-3] + "] "
                    result += timestamp
                    self._need_timestamp = False
                result += char
                # Set flag to add timestamp after newline
                if char == '\n':
                    self._need_timestamp = True

            self.receive_text.insertPlainText(result)
            self.receive_text.moveCursor(
                self.receive_text.textCursor().MoveOperation.End
            )
        except Exception as e:
            self.receive_text.insertPlainText(f"[Decode error: {e}]")

    def _on_error(self, error_msg: str) -> None:
        """Handle error from serial worker."""
        self.status_bar.showMessage(f"Error: {error_msg}")
        QMessageBox.critical(self, "Serial Error", error_msg)

    def _clear_receive(self) -> None:
        """Clear the receive text area."""
        self.receive_text.clear()
        self._need_timestamp = True  # Reset timestamp flag after clearing

    def _clear_history(self) -> None:
        """Clear the command history."""
        self.history_list.clear()

    def _load_settings(self) -> None:
        """Load saved settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        baudrate = self.settings.value("baudrate", "115200")
        index = self.baudrate_combo.findText(baudrate)
        if index >= 0:
            self.baudrate_combo.setCurrentIndex(index)

        line_ending = self.settings.value("line_ending", "CR+LF")
        index = self.newline_combo.findText(line_ending)
        if index >= 0:
            self.newline_combo.setCurrentIndex(index)

        # Load last used port (will be applied after refresh_ports)
        self._last_port = self.settings.value("port", "")

        # Load batch send content and interval
        batch_content = self.settings.value("batch_content", "")
        if batch_content:
            self.batch_text.setPlainText(batch_content)
        batch_interval = self.settings.value("batch_interval", 100, type=int)
        self.interval_spin.setValue(batch_interval)

        # Load history
        history = self.settings.value("history", [])
        if history:
            for item in history:
                self.history_list.addItem(item)

    def _save_settings(self) -> None:
        """Save settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("port", self.port_combo.currentData() or "")
        self.settings.setValue("baudrate", self.baudrate_combo.currentText())
        self.settings.setValue("line_ending", self.newline_combo.currentText())

        # Save batch send content and interval
        self.settings.setValue("batch_content", self.batch_text.toPlainText())
        self.settings.setValue("batch_interval", self.interval_spin.value())

        # Save history
        history = []
        for i in range(min(self.history_list.count(), 100)):
            history.append(self.history_list.item(i).text())
        self.settings.setValue("history", history)

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self._save_settings()
        self.serial_worker.stop()
        event.accept()