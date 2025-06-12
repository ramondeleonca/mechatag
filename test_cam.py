import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

ret, frame = cap.read()
if not ret:
    print("Failed to grab frame")
    exit()

print("Captured frame size:", frame.shape)
