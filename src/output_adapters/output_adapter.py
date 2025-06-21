from abc import ABC, abstractmethod

class OutputAdapter(ABC):
    @abstractmethod
    def write(self, data) -> None:
        """Send data to the output."""
        pass

    @abstractmethod
    def open(self) -> None:
        """Open the output connection."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the output connection."""
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """Check if the output connection is open."""
        pass