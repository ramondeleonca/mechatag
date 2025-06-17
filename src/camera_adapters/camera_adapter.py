from abc import ABC, abstractmethod
import numpy as np

class CameraAdapter:
    @abstractmethod
    def get_frame(self) -> np.ndarray:
        pass