import cv2
import flask
from flask_cors import CORS

# Set up server
app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/video')
def video_feed():
    def generate_frames():
        camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
        while True:
            success, frame = camera.read()
            if not success:
                continue
            else:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                
                # Yield the frame in the correct format for streaming
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
    return flask.Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the server
app.run("0.0.0.0", port=8000)