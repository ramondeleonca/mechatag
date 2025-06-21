from abc import ABC, abstractmethod
import numpy as np

class CameraAdapter(ABC):
    @abstractmethod
    def get_frame(self) -> np.ndarray:
        pass