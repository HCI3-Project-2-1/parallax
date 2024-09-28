# face_tracker.py

import cv2
import mediapipe as mp
import socket
import time

# Constants
UDP_IP = "127.0.0.1"  # Godot listening on localhost
UDP_PORT = 12345
ALPHA = 0.3  # Smoothing factor for low-pass filter

# Initialize MediaPipe Face Mesh for more detailed facial landmarks
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

def smooth_coordinates(new_x, new_y, prev_x, prev_y, alpha):
    """Smooth the coordinates using exponential smoothing."""
    if prev_x is None or prev_y is None:
        return new_x, new_y
    smoothed_x = alpha * new_x + (1 - alpha) * prev_x
    smoothed_y = alpha * new_y + (1 - alpha) * prev_y
    return smoothed_x, smoothed_y

def send_coordinates(sock, x, y):
    """Send normalized coordinates to Godot via UDP."""
    message = f"{x:.4f},{y:.4f}"
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

def main():
    """Main function to run the face tracking."""
    # Initialize UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Initialize variables
    smoothed_x, smoothed_y = None, None

    # Start capturing video
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    # Variables for performance measurement
    frame_count = 0
    start_time = time.time()

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,  # Includes iris landmarks
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break

                # Convert the BGR image to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Process the image and detect face mesh
                results = face_mesh.process(rgb_frame)

                if results.multi_face_landmarks:
                    # Process the first face
                    face_landmarks = results.multi_face_landmarks[0]
                    h, w, _ = frame.shape

                    # Use the nose tip landmark as a reference point
                    nose_tip = face_landmarks.landmark[1]  # Nose tip index
                    x = int(nose_tip.x * w)
                    y = int(nose_tip.y * h)

                    # Smooth the coordinates
                    smoothed_x, smoothed_y = smooth_coordinates(x, y, smoothed_x, smoothed_y, ALPHA)

                    # Normalize coordinates to range -1 to 1
                    norm_x = (smoothed_x / w) * 2 - 1
                    norm_y = -((smoothed_y / h) * 2 - 1)  # Invert Y-axis to match coordinate system

                    # Send the normalized coordinates to Godot via UDP
                    send_coordinates(sock, norm_x, norm_y)

                    # Draw the face mesh annotations on the frame
                    mp_drawing.draw_landmarks(
                        frame,
                        face_landmarks,
                        mp_face_mesh.FACEMESH_CONTOURS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1)
                    )

                    # Mark the nose tip
                    cv2.circle(frame, (int(smoothed_x), int(smoothed_y)), 5, (255, 0, 0), -1)
                    cv2.putText(frame, f"({norm_x:.2f}, {norm_y:.2f})", (x + 10, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                else:
                    # No face detected; you might want to send a default value or handle accordingly
                    pass

                # Display the frame
                cv2.imshow('Face Tracking', frame)

                # Performance measurement
                frame_count += 1
                elapsed_time = time.time() - start_time
                fps = frame_count / elapsed_time
                cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Release resources
            cap.release()
            cv2.destroyAllWindows()
            sock.close()
            print(f"Average FPS: {fps:.2f}")

if __name__ == "__main__":
    main()
