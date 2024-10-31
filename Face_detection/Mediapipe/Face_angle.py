import cv2
import mediapipe as mp
import socket
import time
from timeit import default_timer as timer
import threading
from collections import deque
import numpy as np

class FaceAndGestureTracker:
    def __init__(self):
        print('-' * 15 + '*' * 15 + '-' * 15)
        print('-' * 14 + 'Initializing FaceAndGestureTracker' + '-' * 15)
        print('-' * 15 + '*' * 15 + '-' * 15)

        # Initialize constants
        self.UDP_IP = "127.0.0.1"
        self.UDP_PORT = 12345
        self.ALPHA = 0.7
        self.FOCAL_LENGTH = 615
        self.FACE_WIDTH_CM = 14

        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_landmarker = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Initialize MediaPipe Hands for gesture recognition
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Initialize MediaPipe Drawing Utils
        self.mp_drawing = mp.solutions.drawing_utils

        # Initialize Kalman Filter for x, y, z
        self.kalman_x = cv2.KalmanFilter(2, 1)
        self.kalman_x.measurementMatrix = np.array([[1, 0]], np.float32)
        self.kalman_x.transitionMatrix = np.array([[1, 1],
                                                   [0, 1]], np.float32)
        self.kalman_x.processNoiseCov = np.array([[1, 0],
                                                 [0, 1]], np.float32) * 0.03

        self.kalman_y = cv2.KalmanFilter(2, 1)
        self.kalman_y.measurementMatrix = np.array([[1, 0]], np.float32)
        self.kalman_y.transitionMatrix = np.array([[1, 1],
                                                   [0, 1]], np.float32)
        self.kalman_y.processNoiseCov = np.array([[1, 0],
                                                 [0, 1]], np.float32) * 0.03

        self.kalman_z = cv2.KalmanFilter(2, 1)
        self.kalman_z.measurementMatrix = np.array([[1, 0]], np.float32)
        self.kalman_z.transitionMatrix = np.array([[1, 1],
                                                   [0, 1]], np.float32)
        self.kalman_z.processNoiseCov = np.array([[1, 0],
                                                 [0, 1]], np.float32) * 0.03

        # Initialize global variables
        self.smoothed_x, self.smoothed_y, self.smoothed_z = None, None, None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.eye_center_coords = None
        self.fps = 0
        self.udp_packet_count = 0
        self.current_udp_packets_per_sec = 0
        self.last_udp_count_time = time.time()
        self.frame_processed = threading.Event()
        self.coordinates = (None, None)
        self.gesture = False  # Changed from None to False (bool)

        # Initialize filtered coordinates
        self.filtered_x = None
        self.filtered_y = None
        self.filtered_z = None

    def smooth_coordinates(self, new_x, new_y, new_z, prev_x, prev_y, prev_z):
        """Smooth the coordinates using exponential smoothing."""
        if prev_x is None or prev_y is None or prev_z is None:
            return new_x, new_y, new_z
        smoothed_x = self.ALPHA * new_x + (1 - self.ALPHA) * prev_x
        smoothed_y = self.ALPHA * new_y + (1 - self.ALPHA) * prev_y
        smoothed_z = self.ALPHA * new_z + (1 - self.ALPHA) * prev_z
        return smoothed_x, smoothed_y, smoothed_z

    def send_coordinates(self, x, y, z, gesture):
        """Send normalized coordinates, distance, and gesture to Godot via UDP."""
        self.udp_packet_count += 1
        # Convert boolean to integer (1 for True, 0 for False)
        gesture_int = 1 if gesture else 0
        message = f"{x:.4f},{y:.4f},{z:.4f},{gesture_int}"
        self.sock.sendto(message.encode(), (self.UDP_IP, self.UDP_PORT))

    def capture_frames(self, cap, frame_deque):
        """Capture frames in a separate thread."""
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if len(frame_deque) < 2:
                frame_deque.append(frame)
            self.frame_processed.wait()
            self.frame_processed.clear()

    def estimate_distance(self, face_width_pixels, image_width):
        """Estimate the distance of the face from the camera."""
        face_width_pixels = max(1, face_width_pixels)
        distance = (self.FACE_WIDTH_CM * self.FOCAL_LENGTH) / (face_width_pixels * 0.1)
        return distance

    def is_victory_gesture(self, hand_landmarks):
        """Determine if the hand landmarks correspond to a 'victory' gesture."""
        # Simple heuristic: only index and middle fingers are up
        # Tip landmarks indices for fingers
        FINGER_TIPS = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky

        fingers_up = 0
        for tip_id in FINGER_TIPS[:2]:  # Check only index and middle fingers
            if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
                fingers_up += 1

        # Check if only index and middle fingers are up
        if fingers_up == 2:
            # Further checks can be added for better accuracy
            return True
        else:
            return False

    def process_face_results(self, results, output_image, timestamp_ms):
        """Process the face landmarker result."""
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = output_image.shape
                # Draw face mesh using drawing_utils
                self.mp_drawing.draw_landmarks(
                    image=output_image,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
                )

                # Corrected: Accessing the first nose landmark
                # Assuming FACEMESH_NOSE is a list of indices
                # You may need to verify the correct index for the nose tip
                nose_tip_index = 1  # Example index, replace with actual if different
                nose_tip = face_landmarks.landmark[nose_tip_index]
                x = int(nose_tip.x * w)
                y = int(nose_tip.y * h)
                distance = self.estimate_distance(abs(face_landmarks.landmark[234].x - face_landmarks.landmark[454].x) * w, w)
                norm_x = (nose_tip.x) * 2 - 1
                norm_y = -(nose_tip.y * 2 - 1)
                norm_z = (distance - 30) / 100

                # Update Kalman Filters
                measured_x = np.array([[np.float32(norm_x)]])
                self.kalman_x.correct(measured_x)
                pred_x = self.kalman_x.predict()
                self.filtered_x = pred_x[0][0]

                measured_y = np.array([[np.float32(norm_y)]])
                self.kalman_y.correct(measured_y)
                pred_y = self.kalman_y.predict()
                self.filtered_y = pred_y[0][0]

                measured_z = np.array([[np.float32(norm_z)]])
                self.kalman_z.correct(measured_z)
                pred_z = self.kalman_z.predict()
                self.filtered_z = pred_z[0][0]

                # Placeholder for gesture (to be updated in hand results)
                gesture = self.gesture  # Already a bool

                self.send_coordinates(self.filtered_x, self.filtered_y, self.filtered_z, gesture)

        self.frame_processed.set()

    def process_hand_results(self, results, output_image):
        """Process the hand landmarker result."""
        self.gesture = False  # Reset gesture to False
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks using drawing_utils
                self.mp_drawing.draw_landmarks(
                    image=output_image,
                    landmark_list=hand_landmarks,
                    connections=self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=1),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=1)
                )

                # Determine gesture
                detected_gesture = self.is_victory_gesture(hand_landmarks)
                if detected_gesture:
                    self.gesture = True
                    # You can add additional annotations or actions here
                    # For example, draw text on the image
                    cv2.putText(output_image, "Victory!", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    def run(self, fps_interval=1):
        """Main function to run the face and gesture tracking."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return

        frame_deque = deque(maxlen=100)
        capture_thread = threading.Thread(target=self.capture_frames, args=(cap, frame_deque))
        capture_thread.daemon = True
        capture_thread.start()
        frame_count = 0
        start_time = timer()
        interval_start_time = start_time
        interval_frame_count = 0

        try:
            while True:
                current_time = time.time()
                if current_time - self.last_udp_count_time >= 1.0:
                    self.current_udp_packets_per_sec = self.udp_packet_count
                    self.udp_packet_count = 0
                    self.last_udp_count_time = current_time

                if not frame_deque:
                    continue

                frame = frame_deque.popleft()
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Process face landmarks
                face_results = self.face_landmarker.process(rgb_frame)
                self.process_face_results(face_results, frame, int(time.time() * 1000))

                # Process hand landmarks
                hand_results = self.hands.process(rgb_frame)
                self.process_hand_results(hand_results, frame)

                frame_count += 1
                interval_frame_count += 1
                interval_elapsed_time = timer() - interval_start_time

                # Update FPS every interval
                if interval_elapsed_time >= fps_interval:
                    self.fps = interval_frame_count / interval_elapsed_time
                    interval_start_time = timer()
                    interval_frame_count = 0

                # Display FPS and UDP statistics
                cv2.putText(frame, f'FPS: {self.fps:.2f}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f'UDP Packets/sec: {self.current_udp_packets_per_sec}', (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                cv2.imshow('Face and Gesture Tracking', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.sock.close()
            print(f"Average FPS: {self.fps:.2f}")
            print(f"UDP Packets/sec: {self.current_udp_packets_per_sec}")

if __name__ == "__main__":
    tracker = FaceAndGestureTracker()
    tracker.run()
