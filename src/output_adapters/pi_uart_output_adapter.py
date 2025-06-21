from output_adapter import OutputAdapter
from serial import Serial

class PiUARTOutputAdapter(OutputAdapter):
    serial: Serial

    def __init__(self, port: str = "/dev/serial0", baudrate: int = 115200):
        self.serial = Serial(port, baudrate, timeout=1)

    def write(self, data: str) -> None:
        """Send data to the UART port."""
        if self.serial.is_open:
            self.serial.write(data.encode('utf-8'))
        else:
            raise RuntimeError("UART port is not open")

    def open(self) -> None:
        """Open the UART connection."""
        if not self.serial.is_open:
            self.serial.open()

    def close(self) -> None:
        """Close the UART connection."""
        if self.serial.is_open:
            self.serial.close()

    def is_open(self) -> bool:
        """Check if the UART connection is open."""
        return self.serial.is_open