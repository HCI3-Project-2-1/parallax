# face_tracker_dnn.py

import cv2
import socket
import time
import numpy as np

# Constants
UDP_IP = "127.0.0.1"  # Godot listening on localhost
UDP_PORT = 12345
ALPHA = 0.3  # Smoothing factor for low-pass filter
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for detections

# Paths to model files
PROTO_TEXT = "deploy.prototxt.txt"
MODEL_WEIGHTS = "res10_300x300_ssd_iter_140000.caffemodel"

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
    """Main function to run the face tracking using OpenCV DNN."""
    # Initialize UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Load the pre-trained face detection model
    net = cv2.dnn.readNetFromCaffe(PROTO_TEXT, MODEL_WEIGHTS)

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

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            h, w = frame.shape[:2]

            # Preprocess the frame for the DNN
            blob = cv2.dnn.blobFromImage(
                cv2.resize(frame, (300, 300)),
                1.0,
                (300, 300),
                (104.0, 177.0, 123.0)
            )

            net.setInput(blob)
            detections = net.forward()

            max_confidence = 0
            face_box = None

            # Loop over the detections
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence > CONFIDENCE_THRESHOLD and confidence > max_confidence:
                    max_confidence = confidence
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    face_box = box.astype("int")

            if face_box is not None:
                (startX, startY, endX, endY) = face_box
                x = (startX + endX) // 2
                y = (startY + endY) // 2

                # Smooth the coordinates
                smoothed_x, smoothed_y = smooth_coordinates(x, y, smoothed_x, smoothed_y, ALPHA)

                # Normalize coordinates to range -1 to 1
                norm_x = (smoothed_x / w) * 2 - 1
                norm_y = -((smoothed_y / h) * 2 - 1)  # Invert Y-axis to match coordinate system

                # Send the normalized coordinates to Godot via UDP
                send_coordinates(sock, norm_x, norm_y)

                # Draw the bounding box and center point
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                cv2.circle(frame, (int(smoothed_x), int(smoothed_y)), 5, (0, 0, 255), -1)
                cv2.putText(frame, f"({norm_x:.2f}, {norm_y:.2f})", (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(frame, f"Confidence: {max_confidence:.2f}", (startX, endY + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            else:
                # No face detected; handle accordingly
                pass

            # Mirror the frame
            display_frame = cv2.flip(frame, 1)

            # Performance measurement
            frame_count += 1
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time
            cv2.putText(display_frame, f'FPS: {fps:.2f}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            # Display the frame
            cv2.imshow('Face Tracking DNN', display_frame)

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
