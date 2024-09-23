import cv2
import matplotlib.pyplot as plt
import socket

# Load the pre-trained classifiers for face and eye detection
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

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the frame to grayscale (needed for Haar Cascade)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Clear data for new frame
    x_data.clear()
    y_data.clear()

    # Loop over all detected faces
    for (x, y, w, h) in faces:
        # Get the center of the face
        center_x, center_y = get_face_center(x, y, w, h)

        # Apply the low-pass filter to smooth the coordinates
        smoothed_x, smoothed_y = smooth_coordinates(center_x, center_y, smoothed_x, smoothed_y, alpha)

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

    # Update the line on the graph
    line.set_data(x_data, y_data)

    # Redraw the matplotlib plot
    plt.pause(0.01)  # Pause to allow the plot to update

    # Display the resulting frame with detected faces and centers
    cv2.imshow('Face Detection', frame)

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close any OpenCV windows
cap.release()
cv2.destroyAllWindows()
sock.close()


