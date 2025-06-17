from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import robotpy_apriltag

app = Flask(__name__)
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

detector = robotpy_apriltag.AprilTagDetector()
detector.addFamily("tag36h11")

def generate_stream():
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        detections = detector.detect(frame)
        for detection in detections:
            id = detection.getId()
            center = detection.getCenter()
            cv2.putText(frame, str(id), (int(center.x), int(center.y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

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
