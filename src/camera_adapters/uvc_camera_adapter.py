from .camera_adapter import CameraAdapter
import cv2

# TODO: Add support for configuration
class UvcCameraAdapter(CameraAdapter):
    camera: cv2.VideoCapture

    def __init__(self, index: int):
        self.camera = cv2.VideoCapture(index)

    def get_frame(self):
        return self.camera.read()[1]
