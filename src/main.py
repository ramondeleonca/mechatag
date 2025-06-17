import flask
import argparse
import logging
import robotpy_apriltag as apriltag
import utils
import threading
import numpy as np
import cv2
from camera_adapters.camera_adapter import CameraAdapter

#! Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#! CLI args
parser = argparse.ArgumentParser(description="Run the MechaTag processing server.")
parser.add_argument("--uvc", type=int, default=None, help="UVC camera index, use this option to use a USB webcam.")
parser.add_argument("--threads", type=int, default=1, help="Number of threads to use for detecting apriltags.")
parser.add_argument("--families", type=str, default="tag36h11", help="Comma-separated list of apriltag families to use for detection.")
parser.add_argument("--port", type=int, default=8000, help="Port to run the server on. Default is 8000.")
args = parser.parse_args()

#! Create apriltag detector
detector = apriltag.AprilTagDetector()

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

#! Store frame and detection
out_frame: np.ndarray = None

#! Frame processing function
def process():
    while True:
        # Capture frame from camera
        frame = camera.get_frame()
        if frame is None:
            logger.warning("Failed to capture frame from camera.")
            continue

        # Convert frame to grayscale for apriltag detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect apriltags in the frame
        detections = detector.detect(gray)

        # Draw detections on the frame
        for detection in detections:
            id = detection.getId()
            center = detection.getCenter()
            cv2.putText(frame, str(id), (int(center.x), int(center.y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            corners = [[detection.getCorner(i).x, detection.getCorner(i).y] for i in range(4)]
            cv2.polylines(frame, [np.array(corners, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

        
        # Update the output frame
        global out_frame
        out_frame = frame.copy()
        logger.debug(f"Processed frame with {len(detections)} detections.")



#! Create flask app
app = flask.Flask(__name__)

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

@app.route("/")
def index():
    """Serve the main page."""
    return flask.render_template("index.html")

# App thread
def start_app():
    app.run(host="0.0.0.0", port=args.port, use_reloader=False)
app_thread = threading.Thread(target=start_app)

if __name__ == "__main__":
    app_thread.start()
    logger.info(f"Starting server on port {args.port}...")

    # Start processing on main thread
    logger.info("Starting frame processing...")
    process()

    app_thread.join()  # Wait for the app thread to finish
    logger.info("Server stopped.")