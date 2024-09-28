import cv2
import mediapipe as mp
import socket

# Constants
UDP_IP = "127.0.0.1"  # Godot listening on localhost
UDP_PORT = 12345
ALPHA = 0.3  # Smoothing factor

def smooth_coordinates(new_x, new_y, prev_x, prev_y, alpha):
    """Smooth the coordinates using exponential smoothing."""
    if prev_x is None or prev_y is None:
        return new_x, new_y
    smoothed_x = alpha * new_x + (1 - alpha) * prev_x
    smoothed_y = alpha * new_y + (1 - alpha) * prev_y
    return smoothed_x, smoothed_y

def main():
    # Initialize UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Initialize MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils

    # Initialize variables
    smoothed_x, smoothed_y = None, None

    # Start capturing video
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break

                # Convert the BGR image to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Process the image and detect faces
                results = face_detection.process(rgb_frame)

                if results.detections:
                    # Process only the first detection
                    detection = results.detections[0]
                    bboxC = detection.location_data.relative_bounding_box
                    h, w, _ = frame.shape
                    x1 = int(bboxC.xmin * w)
                    y1 = int(bboxC.ymin * h)
                    w_box = int(bboxC.width * w)
                    h_box = int(bboxC.height * h)

                    # Calculate face center
                    center_x = x1 + w_box // 2
                    center_y = y1 + h_box // 2

                    # Smooth the coordinates
                    smoothed_x, smoothed_y = smooth_coordinates(center_x, center_y, smoothed_x, smoothed_y, ALPHA)

                    # Normalize coordinates to range -1 to 1
                    norm_x = (smoothed_x / w) * 2 - 1
                    norm_y = -((smoothed_y / h) * 2 - 1)  # Invert Y-axis to match coordinate system

                    # Send the normalized coordinates to Godot via UDP
                    message = f"{norm_x:.4f},{norm_y:.4f}"
                    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

                    # Draw annotations on the frame
                    mp_drawing.draw_detection(frame, detection)
                else:
                    # No face detected; you might want to handle this case
                    pass

                # Display the frame
                cv2.imshow('MediaPipe Face Detection', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            # Release resources
            cap.release()
            cv2.destroyAllWindows()
            sock.close()

if __name__ == "__main__":
    main()
