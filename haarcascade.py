import cv2
import socket

# Load the pre-trained classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# UDP setup to send data to Godot
UDP_IP = "127.0.0.1"  # Godot listening on localhost
UDP_PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a constant resolution to avoid dimension mismatch
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

# Function to return the center of the detected face
def get_face_center(x, y, w, h):
    return x + w // 2, y + h // 2

# Low-pass filter (Exponential Smoothing)
alpha = 0.5  # Smoothing factor (adjustable for responsiveness/smoothness)
smoothed_x, smoothed_y = None, None

def smooth_coordinates(center_x, center_y, smoothed_x, smoothed_y, alpha):
    if smoothed_x is None or smoothed_y is None:
        return center_x, center_y
    return alpha * center_x + (1 - alpha) * smoothed_x, alpha * center_y + (1 - alpha) * smoothed_y

# Use a tracker to avoid redetecting the face in every frame
tracker = cv2.TrackerKCF_create()

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)  # Set constant frame size
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

init_tracking = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # If we're not tracking, perform face detection
    if not init_tracking:
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        # Only initialize tracking if a face is detected
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            tracker = cv2.TrackerKCF_create()  # Reset the tracker
            tracker.init(frame, (x, y, w, h))  # Ensure tracker is initialized with the correct frame size
            init_tracking = True
    else:
        # Update the tracker and get the new position of the face
        success, box = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
        else:
            # If tracking fails, reinitialize detection
            init_tracking = False
            continue  # Skip this frame if tracking failed

    # Ensure x, y, w, h are defined before proceeding
    if 'x' in locals():
        # Compute the center of the face and apply smoothing
        center_x, center_y = get_face_center(x, y, w, h)
        smoothed_x, smoothed_y = smooth_coordinates(center_x, center_y, smoothed_x, smoothed_y, alpha)

        # Normalize coordinates to range -1 to 1
        norm_x = (smoothed_x / frame.shape[1] * 2) - 1
        norm_y = -((smoothed_y / frame.shape[0] * 2) - 1)  # Invert Y-axis

        # Send the normalized coordinates to Godot via UDP
        message = f"{norm_x:.4f},{norm_y:.4f}"
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

        # Visualize (optional, can be removed for better performance)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.circle(frame, (int(smoothed_x), int(smoothed_y)), 5, (0, 255, 0), -1)

    cv2.imshow('Face Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
sock.close()
