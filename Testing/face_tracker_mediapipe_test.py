import cv2
import mediapipe as mp
import socket
import time  # For timestamp
import psutil  # For CPU and memory usage tracking

from Testing.face_tracker_dnn_testing import get_system_info, write_performance_results_to_file
from performance_metrics import PerformanceMetrics # Import your performance metrics class

# Constants
UDP_IP = "127.0.0.1"  # Godot listening on localhost
UDP_PORT = 13456  # Changed to a valid port number
ALPHA = 0.3  # Smoothing factor for low-pass filter
FOCAL_LENGTH = 615  # Estimated focal length for distance calculation
FACE_WIDTH_CM = 14  # Approximate width of a face in centimeters

# Initialize MediaPipe Face Mesh for more detailed facial landmarks
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils


def smooth_coordinates(new_x, new_y, new_z, prev_x, prev_y, prev_z, alpha):
    """Smooth the coordinates using exponential smoothing."""
    if prev_x is None or prev_y is None or prev_z is None:
        return new_x, new_y, new_z
    smoothed_x = alpha * new_x + (1 - alpha) * prev_x
    smoothed_y = alpha * new_y + (1 - alpha) * prev_y
    smoothed_z = alpha * new_z + (1 - alpha) * prev_z
    return smoothed_x, smoothed_y, smoothed_z


def estimate_distance(face_width_pixels):
    """Estimate the distance of the face from the camera in centimeters."""
    face_width_pixels = max(1, face_width_pixels)  # Avoid division by zero
    distance = (FACE_WIDTH_CM * FOCAL_LENGTH) / face_width_pixels
    return distance


def send_coordinates(sock, x, y, z):
    """Send normalized coordinates to Godot via UDP, including a timestamp."""
    timestamp = time.time()  # Add timestamp for latency calculation
    message = f"{timestamp},{x:.4f},{y:.4f},{z:.4f}"  # Message includes timestamp and z
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

    def write_performance_results_to_file(system_info, detection_rate, average_error, jitter_x, jitter_y, fps,
                                          average_cpu,
                                          average_memory, filename='performance_results_MediaPipe.txt'):
        """
        Writes the performance results to a text file.

        :param system_info: Dictionary containing system information
        :param detection_rate: Detection rate of the face tracker
        :param average_error: Average error of the face tracker
        :param jitter_x: Jitter in the x-coordinate
        :param jitter_y: Jitter in the y-coordinate
        :param fps: Frames per second
        :param average_cpu: Average CPU usage
        :param average_memory: Average memory usage
        :param filename: Name of the file to write the results into
        """
        with open(filename, 'w') as file:
            file.write("System Information:\n")
            for key, value in system_info.items():
                file.write(f"{key}: {value}\n")
            file.write("\nPerformance Results For MediaPipe:\n")
            file.write(f"Detection Rate: {detection_rate:.2f}%\n")
            file.write(f"Average Localization Error: {average_error:.2f}\n")
            file.write(f"Jitter X: {jitter_x:.2f}\n")
            file.write(f"Jitter Y: {jitter_y:.2f}\n")
            file.write(f"Average FPS: {fps:.2f}\n")
            file.write(f"Average CPU Usage: {average_cpu:.2f}%\n")
            file.write(f"Average Memory Usage: {average_memory / (1024 ** 2):.2f} MB\n")  # Convert bytes to MB


def main():
    """Main function to run the face tracking."""
    # Initialize UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Initialize variables
    smoothed_x, smoothed_y, smoothed_z = None, None, None

    # Initialize performance metrics
    performance = PerformanceMetrics()

    # Start capturing video
    cap = cv2.VideoCapture(0)  # Replace '0' with your video path if using a video file
    if not cap.isOpened():
        print("Error: Could not open video or webcam")
        return

    fps = 0  # Initialize fps with a default value
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
                    print("End of stream or error reading frame.")
                    break

                h, w, _ = frame.shape

                # Convert the BGR image to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Process the image and detect face mesh
                results = face_mesh.process(rgb_frame)

                face_detected = False
                if results.multi_face_landmarks:
                    # Face detected in this frame
                    face_detected = True

                    # Process the first face
                    face_landmarks = results.multi_face_landmarks[0]

                    # Use the nose tip landmark as a reference point
                    nose_tip = face_landmarks.landmark[1]  # Nose tip index
                    x = int(nose_tip.x * w)
                    y = int(nose_tip.y * h)

                    # Calculate face width using cheek landmarks for distance estimation
                    left_cheek = face_landmarks.landmark[234]
                    right_cheek = face_landmarks.landmark[454]
                    face_width_pixels = abs(left_cheek.x - right_cheek.x) * w
                    distance = estimate_distance(face_width_pixels)  # Calculate z coordinate (distance)

                    # Smooth the coordinates
                    smoothed_x, smoothed_y, smoothed_z = smooth_coordinates(x, y, distance, smoothed_x, smoothed_y, smoothed_z, ALPHA)

                    # Record coordinates for jitter calculation
                    performance.add_coordinates_for_jitter(smoothed_x, smoothed_y)

                    # Normalize coordinates to range -1 to 1
                    norm_x = (smoothed_x / w) * 2 - 1
                    norm_y = -((smoothed_y / h) * 2 - 1)  # Invert Y-axis to match coordinate system
                    norm_z = (smoothed_z - 30) / 100  # Adjust Z to a suitable scale

                    # Send the normalized coordinates to Godot via UDP with timestamp
                    send_coordinates(sock, norm_x, norm_y, norm_z)

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
                    cv2.putText(frame, f"({norm_x:.2f}, {norm_y:.2f}, {norm_z:.2f})", (x + 10, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                # Update performance metrics
                performance.update_detection(face_detected)
                performance.update_cpu_usage()
                performance.update_memory_usage()
                fps = performance.update_fps()  # Ensure FPS is updated here

                # Display the frame with FPS
                cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.imshow('Face Tracking', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Release resources
            cap.release()
            cv2.destroyAllWindows()
            sock.close()

            # Calculate performance metrics
            detection_rate = performance.calculate_detection_rate()
            average_error = performance.calculate_average_error()
            jitter_x, jitter_y = performance.calculate_jitter()
            average_cpu = performance.calculate_average_cpu_usage()
            average_memory = performance.calculate_average_memory_usage()

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
            # write_performance_results_to_file(system_info, detection_rate, average_error, jitter_x, jitter_y, fps,
            #                                  average_cpu, average_memory)


if __name__ == "__main__":
    main()
