import cv2
import socket
import time
import numpy as np
import psutil
from performance_metrics import PerformanceMetrics  # Import your PerformanceMetrics class

# Constants
UDP_IP = "127.0.0.1"  # Godot listening on localhost
UDP_PORT = 13456
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
    """Send normalized coordinates to Godot via UDP, including a timestamp."""
    timestamp = time.time()  # Add timestamp for latency calculation
    message = f"{timestamp},{x:.4f},{y:.4f}"  # Message includes timestamp
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))


def get_system_info():
    """
    Retrieves current system specifications.

    :return: Dictionary containing system information (CPU speed, CPU count, Total memory)
    """
    cpu_speed = psutil.cpu_freq().max  # Max CPU speed in MHz
    system_info = {
        'CPU Speed': f"{cpu_speed / 1000:.2f} GHz",  # Convert MHz to GHz
        'CPU Count': psutil.cpu_count(logical=True),
        'Total Memory': f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB"  # Bytes to GB
    }
    return system_info


def write_performance_results_to_file(system_info, detection_rate, average_error, jitter_x, jitter_y, fps, average_cpu,
                                      average_memory, filename='performance_results_dnn.txt'):
    """
    Writes the performance results to a text file.
    """
    with open(filename, 'w') as file:
        file.write("System Information:\n")
        for key, value in system_info.items():
            file.write(f"{key}: {value}\n")
        file.write("\nPlease provide your username\n")
        file.write("\nPerformance Results For DNN:\n")
        file.write(f"Detection Rate: {detection_rate:.2f}%\n")
        file.write(f"Average Localization Error: {average_error:.2f}\n")
        file.write(f"Jitter X: {jitter_x:.2f}\n")
        file.write(f"Jitter Y: {jitter_y:.2f}\n")
        file.write(f"Average FPS: {fps:.2f}\n")
        file.write(f"Average CPU Usage: {average_cpu:.2f}%\n")
        file.write(f"Average Memory Usage: {average_memory / (1024 ** 2):.2f} MB\n")  # Convert bytes to MB


# Generate static ground truth (face always centered)
def generate_static_ground_truth(frame_width, frame_height):
    """Generate ground truth coordinates assuming the face is always in the center of the frame."""
    center_x = frame_width // 2
    center_y = frame_height // 2
    return center_x, center_y


# Generate moving ground truth (face moves horizontally across the frame)
def generate_moving_ground_truth(frame_width, frame_height, frame_count, total_frames):
    """Generate ground truth coordinates assuming the face moves horizontally across the frame."""
    center_y = frame_height // 2  # Face stays vertically centered
    movement_range = frame_width * 0.8  # Horizontal movement range (80% of frame width)
    center_x = int((frame_count / total_frames) * movement_range + (frame_width * 0.1))
    return center_x, center_y


def main():
    """Main function to run the face tracking using OpenCV DNN."""
    # Initialize UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Load the pre-trained face detection model
    net = cv2.dnn.readNetFromCaffe(PROTO_TEXT, MODEL_WEIGHTS)

    # Initialize variables
    smoothed_x, smoothed_y = None, None

    # Initialize performance metrics
    performance = PerformanceMetrics()
    fps = 0  # Initialize fps to have a starting value

    # Start capturing video (try from file, fallback to webcam if not available)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Video file not found or webcam could not be opened.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap.get(cv2.CAP_PROP_FRAME_COUNT) > 0 else 1  # Avoid zero frames

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of stream or error reading frame.")
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
            face_detected = False

            # Loop over the detections
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence > CONFIDENCE_THRESHOLD and confidence > max_confidence:
                    max_confidence = confidence
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    face_box = box.astype("int")
                    face_detected = True

            if face_box is not None:
                (startX, startY, endX, endY) = face_box
                x = (startX + endX) // 2
                y = (startY + endY) // 2

                # Smooth the coordinates
                smoothed_x, smoothed_y = smooth_coordinates(x, y, smoothed_x, smoothed_y, ALPHA)

                # Record coordinates for jitter calculation
                performance.add_coordinates_for_jitter(smoothed_x, smoothed_y)

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

                # Use static or moving ground truth
                true_x, true_y = generate_moving_ground_truth(w, h, performance.frame_count, total_frames)
                performance.add_localization_error(smoothed_x, smoothed_y, true_x, true_y)

            # Update performance metrics, including CPU and Memory usage
            performance.update_detection(face_detected)
            performance.update_cpu_usage()  # Track CPU usage
            performance.update_memory_usage()  # Track memory usage
            fps = performance.update_fps()  # Update fps and ensure it's always updated and prevent division by zero
            if fps == 0:  # Ensure it does not stay zero
                fps = 1

            # Performance measurement and FPS display
            cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Display the frame
            cv2.imshow('Face Tracking DNN', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        sock.close()

        # Calculate and print detection rate, average localization error, jitter, CPU, and memory usage
        detection_rate = performance.calculate_detection_rate()
        average_error = performance.calculate_average_error()
        jitter_x, jitter_y = performance.calculate_jitter()
        average_cpu = performance.calculate_average_cpu_usage()  # Get the average CPU usage
        average_memory = performance.calculate_average_memory_usage()  # Get the average memory usage

        print(f"Detection Rate: {detection_rate:.2f}%")
        print(f"Average Localization Error: {average_error:.2f}")
        print(f"Jitter X: {jitter_x:.2f}")
        print(f"Jitter Y: {jitter_y:.2f}")
        print(f"Average FPS: {fps:.2f}")
        print(f"Average CPU Usage: {average_cpu:.2f}%")
        print(f"Average Memory Usage: {average_memory / (1024 ** 2):.2f} MB")

        # Get system information
        system_info = get_system_info()

        # Write performance results to file
        write_performance_results_to_file(system_info, detection_rate, average_error, jitter_x, jitter_y, fps,
                                          average_cpu, average_memory)


if __name__ == "__main__":
    main()