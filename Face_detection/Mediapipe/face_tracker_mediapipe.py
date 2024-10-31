import cv2
import mediapipe as mp
import socket
import time
from timeit import default_timer as timer
import threading
from collections import deque
import numpy as np

class FaceTracker:
    def __init__(self):
        print('-' * 15 + '*' * 15 + '-' * 15)
        print('-' * 14 + 'Initializing FaceTracker' + '-' * 15)
        print('-' * 15 + '*' * 15 + '-' * 15)

        # Initialize constants
        self.UDP_IP = "127.0.0.1"
        self.UDP_PORT = 12345
        self.ALPHA = 0.7
        self.FOCAL_LENGTH = 615
        self.FACE_WIDTH_CM = 14

        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
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

        # Initialize filtered coordinates
        self.filtered_x = None
        self.filtered_y = None
        self.filtered_z = None
    
    # Note: replaced with Kalman Filter
    # def smooth_coordinates(self, new_x, new_y, new_z, prev_x, prev_y, prev_z):
    #     """Smooth the coordinates using exponential smoothing."""
    #     if prev_x is None or prev_y is None or prev_z is None:
    #         return new_x, new_y, new_z
    #     smoothed_x = self.ALPHA * new_x + (1 - self.ALPHA) * prev_x
    #     smoothed_y = self.ALPHA * new_y + (1 - self.ALPHA) * prev_y
    #     smoothed_z = self.ALPHA * new_z + (1 - self.ALPHA) * prev_z
    #     return smoothed_x, smoothed_y, smoothed_z

    def send_coordinates(self, x, y, z):
        """Send normalized coordinates and distance to Godot via UDP."""
        self.udp_packet_count += 1
        message = f"{x:.4f},{y:.4f},{z:.4f}"
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

    def process_result(self, result, output_image, timestamp_ms):
        """Process the face landmarker result."""
        if result.face_landmarks:
            face_landmarks = result.face_landmarks[0]
            
            h, w = output_image.height, output_image.width
            nose_tip = face_landmarks[1]
            x = int(nose_tip.x * w)
            y = int(nose_tip.y * h)
            left_cheek = face_landmarks[234]
            right_cheek = face_landmarks[454]
            face_width_pixels = abs(left_cheek.x - right_cheek.x) * w
            distance = self.estimate_distance(face_width_pixels, w)
            self.eye_center_coords = (x, y-130)
            norm_x = (x / w) * 2 - 1
            norm_y = -((y / h) * 2 - 1)
            norm_z = (distance - 30) / 100

            # Update Kalman Filters
            measured_x = np.array([[np.float32(norm_x)]])
            self.kalman_x.correct(measured_x)
            pred_x = self.kalman_x.predict()
            self.filtered_x = pred_x[0][0]  # Assign to instance variable

            measured_y = np.array([[np.float32(norm_y)]])
            self.kalman_y.correct(measured_y)
            pred_y = self.kalman_y.predict()
            self.filtered_y = pred_y[0][0]  # Assign to instance variable

            measured_z = np.array([[np.float32(norm_z)]])
            self.kalman_z.correct(measured_z)
            pred_z = self.kalman_z.predict()
            self.filtered_z = pred_z[0][0]  # Assign to instance variable

            self.send_coordinates(self.filtered_x, self.filtered_y, self.filtered_z)
        self.frame_processed.set()

    def run(self, fps_interval=1):
        """Main function to run the face tracking."""
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
        base_options = mp.tasks.BaseOptions(model_asset_path='Face_detection/Mediapipe/face_landmarker.task')
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.1,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            result_callback=self.process_result
        )
        with mp.tasks.vision.FaceLandmarker.create_from_options(options) as landmarker:
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
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                    frame_timestamp_ms = int(time.time() * 1000)
                    landmarker.detect_async(mp_image, frame_timestamp_ms)
                    frame_count += 1
                    interval_frame_count += 1
                    interval_elapsed_time = timer() - interval_start_time

                    # Update FPS every N seconds
                    if interval_elapsed_time >= fps_interval:
                        self.fps = interval_frame_count / interval_elapsed_time
                        interval_start_time = timer()
                        interval_frame_count = 0

                    display_frame = cv2.flip(frame, 1)
                    if self.eye_center_coords:
                        mirrored_x = display_frame.shape[1] - self.eye_center_coords[0]
                        cv2.circle(display_frame, (mirrored_x, self.eye_center_coords[1]), 5, (0, 255, 0), -1)
                        cv2.putText(display_frame, f'X: {self.filtered_x:.4f}, Y: {self.filtered_y:.4f}, Z: {self.filtered_z:.4f}', (10, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                    cv2.putText(display_frame, f'FPS: {self.fps:.2f}', (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(display_frame, f'UDP Packets/sec: {self.current_udp_packets_per_sec}', (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.imshow('Face Tracking', display_frame)
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
    tracker = FaceTracker()
    tracker.run()
