import cv2
import mediapipe as mp
import socket
import time
import threading
import queue
import numpy as np
from collections import deque

# Constants
UDP_IP = "127.0.0.1"  # Godot listening on localhost
UDP_PORT = 12345
ALPHA = 0.7  # Smoothing factor for low-pass filter

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Global variables
smoothed_x, smoothed_y = None, None
sock = None
eye_center_coords = None

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

def capture_frames(cap, frame_queue):
    """Capture frames in a separate thread."""
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_queue.qsize() < 2:  # Limit queue size to prevent memory issues
            frame_queue.put(frame)

def process_result(result: mp.tasks.vision.FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    """Process the face landmarker result."""
    global smoothed_x, smoothed_y, sock, eye_center_coords

    if result.face_landmarks:
        face_landmarks = result.face_landmarks[0]
        h, w = output_image.height, output_image.width
        # Use the nose tip landmark as a reference point
        nose_tip = face_landmarks[1]  # Nose tip index
        x = int(nose_tip.x * w)
        y = int(nose_tip.y * h)

        # Assign the nose tip coordinates
        eye_center_coords = (x, y-130) # y-150

        # Smooth the coordinates
        smoothed_x, smoothed_y = smooth_coordinates(x, y, smoothed_x, smoothed_y, ALPHA)

        # Normalize coordinates to range -1 to 1
        norm_x = (smoothed_x / w) * 2 - 1
        norm_y = -((smoothed_y / h) * 2 - 1)  # Invert Y-axis to match coordinate system

        # Send the normalized coordinates to Godot via UDP
        send_coordinates(sock, norm_x, norm_y)
    else:
        eye_center_coords = None

def main():
    """Main function to run the face tracking."""
    global sock, eye_center_coords
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Start capturing video
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    # Set up frame queue and start capture thread
    frame_queue = queue.Queue()
    capture_thread = threading.Thread(target=capture_frames, args=(cap, frame_queue))
    capture_thread.daemon = True
    capture_thread.start()

    # Variables for performance measurement
    frame_count = 0
    start_time = time.time()
    processing_times = deque(maxlen=100)

    # Create FaceLandmarker with live stream mode
    base_options = mp.tasks.BaseOptions(model_asset_path='face_landmarker.task')
    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.1,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        result_callback=process_result
    )

    with mp.tasks.vision.FaceLandmarker.create_from_options(options) as landmarker:
        try:
            while True:
                if frame_queue.empty():
                    continue

                frame = frame_queue.get()
                frame_start_time = time.time()

                # Convert the BGR image to RGB for processing
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                # Process the image asynchronously
                frame_timestamp_ms = int(time.time() * 1000)
                landmarker.detect_async(mp_image, frame_timestamp_ms)

                # Performance measurement
                frame_count += 1
                elapsed_time = time.time() - start_time
                fps = frame_count / elapsed_time
                processing_time = time.time() - frame_start_time
                processing_times.append(processing_time)

                # Create a mirrored frame for display only
                display_frame = cv2.flip(frame, 1)

                # Draw the nose tip on the display frame
                if eye_center_coords:
                    # Flip the x-coordinate for the mirrored display
                    mirrored_x = display_frame.shape[1] - eye_center_coords[0]
                    cv2.circle(display_frame, (mirrored_x, eye_center_coords[1]), 5, (0, 255, 0), -1)

                cv2.putText(display_frame, f'FPS: {fps:.2f}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(display_frame, f'Processing time: {processing_time*1000:.2f} ms', (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                cv2.imshow('Face Tracking', display_frame)

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
            print(f"Average processing time: {np.mean(processing_times)*1000:.2f} ms")
            print(f"Max processing time: {np.max(processing_times)*1000:.2f} ms")

if __name__ == "__main__":
    main()
