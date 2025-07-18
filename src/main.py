import flask
import argparse
import logging
import utils
import threading
import numpy as np
import cv2
import time
import toml
import os
from flask import send_from_directory
from robotpy_apriltag import AprilTagDetector, AprilTagPoseEstimator
from camera_adapters.camera_adapter import CameraAdapter

#! PATHS
DIRNAME = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(DIRNAME, "frontend", "dist")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

#! CLI args
parser = argparse.ArgumentParser(description="Run the MechaTag processing server.")
parser.add_argument("--uvc", type=int, default=None, help="UVC camera index, use this option to use a USB webcam.")
parser.add_argument("--threads", type=int, default=1, help="Number of threads to use for detecting apriltags.")
parser.add_argument("--families", type=str, default="tag36h11", help="Comma-separated list of apriltag families to use for detection.")
parser.add_argument("--port", type=int, default=8000, help="Port to run the server on. Default is 8000.")
args = parser.parse_args()

#! Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log options
logger.info(f"Running with options: {args}")

#! Create apriltag detector
detector = AprilTagDetector()

#! Create apriltag pose estimator
# pose_estimator_config = AprilTagPoseEstimator.Config(0.14)
# pose_estimator = AprilTagPoseEstimator()

# Add families to detector
for family in args.families.split(","):
    family: str = family.strip()
    if family:
        res = detector.addFamily(family)
        if res:
            logger.info(f"Added apriltag family: {family}")
        else:
            logger.error(f"Failed to add apriltag family: {family}. Please check if the family is supported.")

#! Create camera adapter
camera: CameraAdapter
if args.uvc is not None:
    from camera_adapters.uvc_camera_adapter import UvcCameraAdapter
    camera = UvcCameraAdapter(args.uvc)
    logger.info(f"Using UVC camera with index {args.uvc}")
elif not utils.is_pi():
    from camera_adapters.uvc_camera_adapter import UvcCameraAdapter
    camera = UvcCameraAdapter(0)  # Default to first UVC camera if not using Pi
    logger.info("Running on non-Pi system, using UVC camera adapter by default with index 0.")
else:
    from camera_adapters.pi_camera_adapter import PiCameraAdapter
    camera = PiCameraAdapter()
    logger.info("Running on Raspberry Pi, using PiCamera adapter.")

#! Create output adapter

#! Store frame and detection
out_frame: np.ndarray = None

#! Frame processing function
last_process_time = time.time()
def process():
    global out_frame, last_process_time
    while True:
        #* Capture frame from camera
        frame = camera.get_frame()
        if frame is None:
            logger.warning("Failed to capture frame from camera.")
            continue

        # Convert frame to grayscale for apriltag detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #* Detect apriltags in the frame
        detections = detector.detect(gray)

        # Localize
        detections[0]

        
        #* Draw graphics
        # Draw ID
        for detection in detections:
            id = detection.getId()
            center = detection.getCenter()
            cv2.putText(frame, str(id), (int(center.x), int(center.y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            corners = [[detection.getCorner(i).x, detection.getCorner(i).y] for i in range(4)]
            cv2.polylines(frame, [np.array(corners, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

        # Draw FPS
        current_time = time.time()
        fps = 1 / (current_time - last_process_time)
        last_process_time = current_time
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Update the output frame
        out_frame = frame.copy()
        logger.debug(f"Processed frame with {len(detections)} detections.")



#! Create flask app
app = flask.Flask(__name__)

# Serve react frontend
# * Serve static assets (Vite puts them in /assets)
@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(ASSETS_DIR, filename)

# * Serve index.html for everything else (SPA fallback)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return send_from_directory(DIST_DIR, 'index.html')

# Routes
@app.route("/stream")
def stream():
    """Stream video feed with apriltag detections."""
    def generate():
        while True:
            if out_frame is None:
                continue
            ret, jpeg = cv2.imencode(".jpg", out_frame)
            if not ret:
                continue
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n")
    return flask.Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

# App thread
def start_app():
    app.run(host="0.0.0.0", debug=True, port=args.port, use_reloader=False)
app_thread = threading.Thread(target=start_app)

if __name__ == "__main__":
    app_thread.start()
    logger.info(f"Starting server on port {args.port}...")

    # Start processing on main thread
    logger.info("Starting frame processing...")
    process()

    app_thread.join()  # Wait for the app thread to finish
    logger.info("Server stopped.")