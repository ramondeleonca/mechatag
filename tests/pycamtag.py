from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import argparse
import os

app = Flask(__name__)

# Initialize camera
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

def is_pi():
    if os.path.exists('/sys/firmware/devicetree/base/model'):
        with open('/sys/firmware/devicetree/base/model') as f:
            model = f.read()
            return 'pi' in model.lower()
    return False

# Check if running on Raspberry Pi
if is_pi():
    print("Running on a Pi")

# arguments passed to detector
detector_args = {
    "families": "tag36h11",
    "nthreads": 4,
}
if True:
    import pupil_apriltags
    detector = pupil_apriltags.Detector(**detector_args)
else:
    import apriltag
    detector = apriltag.Detector(**detector_args)

def generate_stream():
    while True:
        # Capture frame from camera
        frame = picam2.capture_array()
        # Convert to grayscale for detector
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Detect tags
        detections = detector.detect(gray)
        detections

        for det in detections:
            pts = det.corners.astype(int)
            for i in range(4):
                pt1 = tuple(pts[i])
                pt2 = tuple(pts[(i + 1) % 4])
                cv2.line(frame, pt1, pt2, (0, 0, 255), 2)

            center = tuple(det.center.astype(int))
            tag_id = det.tag_id
            cv2.putText(frame, f"ID:{tag_id}", center, 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=0.7, color=(0, 255, 0), thickness=2)

        ret, jpeg = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + 
               jpeg.tobytes() + 
               b"\r\n")

@app.route("/video")
def video_feed():
    return Response(generate_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
