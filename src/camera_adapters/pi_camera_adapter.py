from .camera_adapter import CameraAdapter
from picamera2 import Picamera2
import cv2

# TODO: Add support for configuration
class PiCameraAdapter(CameraAdapter):
    camera: Picamera2

    def __init__(self):
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_video_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
        self.camera.start()

    def get_frame(self):
        frame = self.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        return frame
