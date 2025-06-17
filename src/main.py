import flask
import util
import argparse
from camera_adapters import camera_adapter
from camera_adapters.pi_camera_adapter import PiCameraAdapter
from camera_adapters.uvc_camera_adapter import UvcCameraAdapter

# CLI args
parser = argparse.ArgumentParser(description="Run the MechaTag processing server.")
# Add uvc argument that takes in an int, autocompletes to 0 if argument present, if not none
parser.add_argument(
    "--uvc",
    type=int,
    default=None,
    help="UVC camera ID (default: None, auto-detects)",
)

# print arguments
args = parser.parse_args()
print(f"Parsed arguments: {args}")
