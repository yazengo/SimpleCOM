"""
Serial communication worker thread module.
Handles serial port reading in a separate thread to keep UI responsive.
"""

from PyQt6.QtCore import QThread, pyqtSignal
import serial
import serial.tools.list_ports
from typing import Optional


class SerialWorker(QThread):
    """Worker thread for handling serial port communication."""

    # Signal emitted when data is received
    data_received = pyqtSignal(bytes)
    # Signal emitted when an error occurs
    error_occurred = pyqtSignal(str)
    # Signal emitted when connection status changes
    connection_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._serial: Optional[serial.Serial] = None
        self._running = False
        self._port = ""
        self._baudrate = 115200

    @staticmethod
    def get_available_ports() -> list[tuple[str, str]]:
        """Scan and return list of available serial ports with descriptions.
        
        Returns:
            List of tuples (device, description), e.g. [("COM4", "USB Serial Port (COM4)")]
        """
        ports = serial.tools.list_ports.comports()
        return [(port.device, f"{port.description}") for port in ports]

    def configure(self, port: str, baudrate: int) -> None:
        """Configure serial port parameters."""
        self._port = port
        self._baudrate = baudrate

    def connect_port(self) -> bool:
        """Open the serial port connection."""
        try:
            if self._serial and self._serial.is_open:
                self._serial.close()

            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1
            )
            self._running = True
            self.connection_changed.emit(True)
            return True
        except serial.SerialException as e:
            self.error_occurred.emit(f"Failed to open port: {str(e)}")
            return False

    def disconnect_port(self) -> None:
        """Close the serial port connection."""
        self._running = False
        if self._serial and self._serial.is_open:
            try:
                self._serial.close()
            except Exception:
                pass
        self.connection_changed.emit(False)

    def is_connected(self) -> bool:
        """Check if serial port is connected."""
        return self._serial is not None and self._serial.is_open

    def send_data(self, data: bytes) -> bool:
        """Send data through serial port."""
        if not self.is_connected():
            self.error_occurred.emit("Serial port is not connected")
            return False

        try:
            self._serial.write(data)
            return True
        except serial.SerialException as e:
            self.error_occurred.emit(f"Failed to send data: {str(e)}")
            return False

    def run(self) -> None:
        """Thread main loop - continuously read from serial port."""
        while self._running:
            if self._serial and self._serial.is_open:
                try:
                    if self._serial.in_waiting > 0:
                        data = self._serial.read(self._serial.in_waiting)
                        if data:
                            self.data_received.emit(data)
                except serial.SerialException as e:
                    self.error_occurred.emit(f"Read error: {str(e)}")
                    self._running = False
                    self.connection_changed.emit(False)
                    break
            self.msleep(10)  # Small delay to prevent CPU overuse

    def stop(self) -> None:
        """Stop the worker thread."""
        self._running = False
        self.disconnect_port()
        self.wait()

