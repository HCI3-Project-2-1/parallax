from dataclasses import dataclass
import cv2
import mediapipe as mp
import threading
import time
import socket


@dataclass
class FaceTrackerState:
    """Tracks the state of the face tracker."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0  # Mediapipe Face Detection doesn't support depth
    avg_fps: float = 0.0  # Average FPS for performance monitoring


class FaceTracker:
    def __init__(self, udp_receiver_ip=None, udp_receiver_port=None):
        """
        Initialize the FaceTracker with optional UDP receiver details.
        Args:
            udp_receiver_ip (str): IP address for sending tracking data via UDP.
            udp_receiver_port (int): Port for sending tracking data via UDP.
        """
        self.udp_receiver_ip = udp_receiver_ip
        self.udp_receiver_port = udp_receiver_port

        self.state = FaceTrackerState()
        self.stop_event = threading.Event()
        self.cap = None

        # Mediapipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils

        # Create and bind the UDP socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.udp_receiver_port:
            try:
                self.udp_socket.bind(("0.0.0.0", udp_receiver_port))  # Bind to the specified port
                print(f"UDP socket bound to port {udp_receiver_port}")
            except Exception as e:
                print(f"Failed to bind UDP socket: {e}")

    def _setup_camera(self):
        """Set up the camera."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open the camera.")

    def run(self):
        """Main loop for running the face tracker."""
        print("Starting FaceTracker...")
        self._setup_camera()

        try:
            with self.mp_face_detection.FaceDetection(
                model_selection=0,  # Short-range model for faces within 2 meters
                min_detection_confidence=0.5
            ) as face_detection:
                while not self.stop_event.is_set():
                    ret, frame = self.cap.read()
                    if not ret or frame is None:
                        print("No frame available.")
                        continue

                    start_time = time.time()

                    # Process the frame and update the state
                    self._process_frame(frame, face_detection)
                    self.state.avg_fps = 1.0 / (time.time() - start_time)

                    # Display the frame with optional overlay
                    cv2.imshow("Face Tracker", frame)

                    # Exit if 'q' key is pressed
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        self.stop()

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.stop()

    def _process_frame(self, frame, face_detection):
        """Process a single frame for face detection."""
        try:
            # Convert frame to RGB as Mediapipe requires it
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Perform face detection
            results = face_detection.process(rgb_frame)

            # Process detections if any faces are found
            if results.detections:
                detection = results.detections[0]  # Only process the first detected face
                self._update_state_with_detection(detection, frame.shape[:2])

                # Optionally draw face detection annotations
                self.mp_drawing.draw_detection(frame, detection)
            else:
                print("No face detected.")
        except Exception as e:
            print(f"Error processing frame: {e}")

    def _update_state_with_detection(self, detection, frame_shape):
        """Update the tracker state based on face detection results."""
        keypoints = detection.location_data.relative_keypoints
        frame_width, frame_height = frame_shape[1], frame_shape[0]

        # Use the nose tip as the main reference point
        nose = keypoints[self.mp_face_detection.FaceKeyPoint.NOSE_TIP]
        self.state.x = nose.x * frame_width
        self.state.y = nose.y * frame_height
        self.state.z = 0.0  # Depth information is unavailable in this model

        print(f"Face position: x={self.state.x:.2f}, y={self.state.y:.2f}, z={self.state.z:.2f}")

        # Send the normalized data via UDP
        self._send_udp_data((self.state.x, self.state.y, self.state.z))

    def _send_udp_data(self, coords):
        """Send normalized coordinates and timestamp to the receiver via UDP."""
        x, y, z = coords
        timestamp = int(time.time() * 1000)  # Current time in milliseconds
        message = f"{timestamp} {x:.4f} {y:.4f} {z:.4f}"
        try:
            self.udp_socket.sendto(message.encode(), (self.udp_receiver_ip, self.udp_receiver_port))
            print(f"Sent UDP data: {message}")
        except Exception as e:
            print(f"UDP send error: {e}")

    def stop(self):
        """Stop the tracker and release resources."""
        self.stop_event.set()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.udp_socket.close()
        cv2.destroyAllWindows()
        print("FaceTracker stopped.")


# Allow standalone execution
if __name__ == "__main__":
    tracker = FaceTracker(udp_receiver_ip="127.0.0.1", udp_receiver_port=6969)
    try:
        tracker.run()
    except KeyboardInterrupt:
        tracker.stop()
