import cv2
import mediapipe as mp
import socket

# UDP setup to send data to Godot
UDP_IP = "127.0.0.1"  # Godot listening on localhost
UDP_PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Set up Face Detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# Low-pass filter (Exponential Smoothing)
alpha = 0.8  # Smoothing factor (adjustable for responsiveness/smoothness)
smoothed_x, smoothed_y = None, None

def smooth_coordinates(center_x, center_y, smoothed_x, smoothed_y, alpha):
    if smoothed_x is None or smoothed_y is None:
        return center_x, center_y
    return alpha * center_x + (1 - alpha) * smoothed_x, alpha * center_y + (1 - alpha) * smoothed_y

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the BGR image to RGB as MediaPipe requires RGB input
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and detect faces
    results = face_detection.process(rgb_frame)

    if results.detections:
        # Get the first detected face
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            h, w, _ = frame.shape
            x, y, w_box, h_box = int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h)

            # Calculate face center
            center_x = x + w_box // 2
            center_y = y + h_box // 2
            smoothed_x, smoothed_y = smooth_coordinates(center_x, center_y, smoothed_x, smoothed_y, alpha)

            # Normalize coordinates to range -1 to 1
            norm_x = (smoothed_x / frame.shape[1] * 2) - 1
            norm_y = -((smoothed_y / frame.shape[0] * 2) - 1)  # Invert Y-axis

            # Send the normalized coordinates to Godot via UDP
            message = f"{norm_x:.4f},{norm_y:.4f}"
            sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

            # Draw face detection annotations on the frame
            mp_drawing.draw_detection(frame, detection)

    # Show the video frame with face detections
    cv2.imshow('MediaPipe Face Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
sock.close()
