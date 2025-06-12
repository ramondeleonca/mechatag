import cv2
import flask
from flask import Response
from flask_cors import CORS

cap = cv2.VideoCapture(0)

# Set up server
app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/video')
def video_feed():
    def generate_frames():
        while True:
            success, frame = cap.read()
            if not success:
                continue
            else:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                
                # Yield the frame in the correct format for streaming
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/still')
def still():
    ret, frame = cap.read()
    if not ret:
        return "Failed to capture image", 500
    
    # Encode frame as JPEG
    ret, jpeg = cv2.imencode('.jpg', frame)
    if not ret:
        return "Failed to encode image", 500

    return Response(jpeg.tobytes(), mimetype='image/jpeg')

# Run the server
app.run("0.0.0.0", port=8000)