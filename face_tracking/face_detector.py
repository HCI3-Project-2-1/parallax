from dataclasses import dataclass
import cv2
import mediapipe as mp
import threading
import time
import ui
import camera_manager
import utils

@dataclass
class FaceDetectorState:
    godot_x: float = 0.0
    godot_y: float = 0.0
    estimated_z: float = 0.0
    image_x: int = 0
    image_y: int = 0

class FaceDetector:
    def __init__(self, udp_receiver_ip=None, udp_receiver_port=None, face_detector_file=None, video_file=None, log_file=None, frame_delay_secs=None):
        self.udp_receiver_ip = udp_receiver_ip
        self.udp_receiver_port = udp_receiver_port
                
        self.state = FaceDetectorState()
        self.ui_config = ui.UiConfig()
        
        self.video_file = video_file
        self.log_file = log_file
        self.frame_delay_secs = frame_delay_secs

        if self.video_file:
            self.capture = cv2.VideoCapture(self.video_file)
        else:
            self.capture = None
            self.camera = camera_manager.CameraManager()

        self.stop_event = threading.Event()
        
        self.detector_options = mp.tasks.vision.FaceDetectorOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=face_detector_file),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            min_detection_confidence=0.7)

        self.mp_face_detector = mp.tasks.vision.FaceDetector

    def run(self):
        if self.video_file:
            with self.mp_face_detector.create_from_options(self.detector_options) as detector:
                while not self.stop_event.is_set():
                    ret, frame = self.capture.read()
                    if not ret:
                        print("video ended or no frame available")
                        break

                    self._process_frame(frame, detector)

                    if self.ui_config.show_overlay:
                        ui.draw_overlay(self, frame)
                    cv2.imshow(self.ui_config.frame_title, frame)
                    
                    if self.frame_delay_secs:
                        time.sleep(self.frame_delay_secs)

                    if self.udp_receiver_ip and self.udp_receiver_port:
                        utils.send_udp_data(self.udp_receiver_ip, self.udp_receiver_port, (self.state.godot_x, self.state.godot_y, self.state.estimated_z))
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key != 255:
                        self.handle_key_event(chr(key))
        else:
            self.camera.start()
            with self.mp_face_detector.create_from_options(self.detector_options) as detector:
                while not self.stop_event.is_set():
                    frame = self.camera.current_frame
                    if frame is None:
                        print("no frame available")
                        continue
                    
                    self._process_frame(frame, detector)

                    if self.ui_config.show_overlay:
                        ui.draw_overlay(self, frame)
                    cv2.imshow(self.ui_config.frame_title, frame)

                    if self.frame_delay_secs:
                        time.sleep(self.frame_delay_secs)
                    
                    if self.udp_receiver_ip and self.udp_receiver_port:
                        utils.send_udp_data(self.udp_receiver_ip, self.udp_receiver_port, (self.state.godot_x, self.state.godot_y, self.state.estimated_z))
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key != 255:
                        self.handle_key_event(chr(key))

    def _process_frame(self, frame, detector=None):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        if not detector:
            print("no detector provided")
            return

        if self.video_file:    
            start_time = time.time()
            results = detector.detect(mp_image)
            exec_time_us = int((time.time() - start_time) * 1_000_000)
            with open(self.log_file, 'a') as f:
                f.write(f"{exec_time_us}\n")
        else:
            results = detector.detect(mp_image)

        if not results.detections:
            print("no face detected")
            return
        
        (eye_midpoint_x, eye_midpoint_y) = utils.extract_eye_midpoint(results.detections[0], frame.shape)
        
        self.state.image_x = eye_midpoint_x
        self.state.image_y = eye_midpoint_y
        
        (godot_x, godot_y) = utils.transform_to_godot_coords(eye_midpoint_x, eye_midpoint_y, frame.shape)

        self.state.godot_x = godot_x
        self.state.godot_y = godot_y


    def handle_key_event(self, key: str):
        if key == 'o':
            self.ui_config.show_overlay = not self.ui_config.show_overlay
        elif key == 'q':
            self.stop()

    def stop(self):
        self.stop_event.set()
        if self.capture:
            self.capture.release()
        else:
            self.camera.stop()

        cv2.destroyAllWindows()

