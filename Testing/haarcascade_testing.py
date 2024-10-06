import cv2
import matplotlib.pyplot as plt
import socket
import time
import os
import platform
import psutil
from performance_metrics import PerformanceMetrics

# Initialize performance metrics class
metrics = PerformanceMetrics()

# Load the pre-trained classifiers for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# UDP setup to send data to Unity
UDP_IP = "127.0.0.1"  # Unity listening on localhost
UDP_PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Function to return the center of the detected face
def get_face_center(x, y, w, h):
    center_x = x + w // 2
    center_y = y + h // 2
    return center_x, center_y


# Low-pass filter (Exponential Smoothing)
alpha = 0.5  # Smoothing factor (adjustable)
smoothed_x, smoothed_y = None, None


def smooth_coordinates(center_x, center_y, smoothed_x, smoothed_y, alpha):
    if smoothed_x is None or smoothed_y is None:
        smoothed_x, smoothed_y = center_x, center_y
    else:
        smoothed_x = alpha * center_x + (1 - alpha) * smoothed_x
        smoothed_y = alpha * center_y + (1 - alpha) * smoothed_y
    return smoothed_x, smoothed_y


def get_system_specs():
    cpu_freq = psutil.cpu_freq()
    processor_details = f"{cpu_freq.current:.2f}GHz" if cpu_freq else "Unknown"
    memory_info = psutil.virtual_memory()
    memory_total_mb = memory_info.total // (1024 ** 2)
    return processor_details, f"{memory_total_mb}MB RAM"


def save_metrics_to_file(metrics, file_path, user_name, processor_details, memory_details):
    # Calculate and get all the performance metrics
    fps = metrics.update_fps()
    detection_rate = metrics.calculate_detection_rate()
    avg_localization_error = metrics.calculate_average_error()
    jitter_x, jitter_y = metrics.calculate_jitter()
    avg_cpu_usage = metrics.calculate_average_cpu_usage()
    avg_memory_usage = metrics.calculate_average_memory_usage()

    # Prepare the text content
    content = (
        f"User Name: {user_name}\n"
        f"Processor: {processor_details}\n"
        f"Memory: {memory_details}\n"
        f"FPS: {fps:.2f}\n"
        f"Detection Rate: {detection_rate:.2f}%\n"
        f"Average Localization Error: {avg_localization_error:.2f}\n"
        f"Jitter - X: {jitter_x:.2f}, Y: {jitter_y:.2f}\n"
        f"Average CPU Usage: {avg_cpu_usage:.2f}%\n"
        f"Average Memory Usage: {avg_memory_usage / (1024 ** 2):.2f} MB\n"  # Convert bytes to MB
    )

    # Save to file
    with open(file_path, 'w') as file:
        file.write(content)

    # Also print the content
    print(content)


def process_video(input_source, user_name):
    global smoothed_x, smoothed_y

    # Get system specifications
    processor_details, memory_details = get_system_specs()

    # Initialize plot data
    x_data, y_data = [], []

    # Create a figure and axis for the live graph
    fig, ax = plt.subplots()
    ax.set_xlim(0, 1920)  # Assuming typical webcam resolution of 1080p
    ax.set_ylim(1080, 0)  # Reverse y-axis for proper display (OpenCV's coordinate system)
    ax.set_xlabel("X Coordinates")
    ax.set_ylabel("Y Coordinates")
    ax.set_title("Face Center Coordinates")

    # Plot initial data
    line, = ax.plot([], [], 'bo')

    # Start capturing video
    cap = cv2.VideoCapture(input_source)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            break

        # Update FPS metric
        fps = metrics.update_fps()

        # Convert the frame to grayscale (needed for Haar Cascade)
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(grey, 1.3, 5)

        # Clear data for new frame
        x_data.clear()
        y_data.clear()

        detected = False

        # Loop over all detected faces
        for (x, y, w, h) in faces:
            detected = True  # Face is detected in this frame

            # Get the center of the face
            center_x, center_y = get_face_center(x, y, w, h)

            # Apply the low-pass filter to smooth the coordinates
            smoothed_x, smoothed_y = smooth_coordinates(center_x, center_y, smoothed_x, smoothed_y, alpha)

            # Calculate localization error assuming the true center is at the original detected coordinates
            metrics.add_localization_error(smoothed_x, smoothed_y, center_x, center_y)

            # Record coordinates for jitter calculation
            metrics.add_coordinates_for_jitter(smoothed_x, smoothed_y)

            # Draw a rectangle around the face and mark its center
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.circle(frame, (int(smoothed_x), int(smoothed_y)), 5, (0, 255, 0), -1)
            cv2.putText(frame, f'Smoothed Center: ({int(smoothed_x)}, {int(smoothed_y)})', (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Append the smoothed center coordinates to the data lists
            x_data.append(smoothed_x)
            y_data.append(smoothed_y)

            # Send the smoothed coordinates to Unity via UDP
            message = f"{int(smoothed_x)},{int(smoothed_y)}"
            sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

        # Update detection frame count
        metrics.update_detection(detected)

        # Update CPU and memory usage
        metrics.update_cpu_usage()
        metrics.update_memory_usage()

        # Update the line on the graph
        line.set_data(x_data, y_data)

        # Redraw the matplotlib plot
        plt.pause(0.01)  # Pause to allow the plot to update

        # Display the resulting frame with detected faces and centers
        cv2.imshow('Face Detection', frame)

        # Check if 'q' or 'Esc' key is pressed to break the loop
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 27 is the Esc key
            break

    # Define the file path for saving metrics
    file_path = os.path.join(os.getcwd(), "performance_metrics_HaarCascade.txt")

    # Save the performance metrics to a file
    save_metrics_to_file(metrics, file_path, user_name, processor_details, memory_details)

    # Release the capture and close any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    sock.close()

# Reminder : USE esc TO EXIT PROGRAM AND TO PRINT RESULTS
def main():
    # For webcam use: 0
    input_source = 0  # Uncomment this line to use the webcam

    # For video file use: "example_video.mp4"
    # input_source = "example_video.mp4"  # Set it to your video file name

    user_name = "User Name"  # Set this to the actual user's name. Anything can be written here like c1 c2 comp 1

    process_video(input_source, user_name)


if __name__ == "__main__":
    main()
