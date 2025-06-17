from camera_adapter import CameraAdapter
from picamera2 import Picamera2

# TODO: Add support for configuration
class PiCameraAdapter(CameraAdapter):
    camera: Picamera2

    def __init__(self):
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_video_configuration(main={"format": "XRGB8888", "size": (640, 480)}))

    def get_frame(self):
        return self.camera.capture_array()
