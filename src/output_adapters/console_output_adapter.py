from output_adapter import OutputAdapter

class ConsoleOutputAdapter(OutputAdapter):
    def __init__(self):
        pass

    def write(self, data: str) -> None:
        """Send data to the console."""
        print(data)

    def open(self) -> None:
        """Open the console output (no action needed)."""
        pass

    def close(self) -> None:
        """Close the console output (no action needed)."""
        pass

    def is_open(self) -> bool:
        """Check if the console output is open."""
        return True