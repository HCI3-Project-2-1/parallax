from dataclasses import dataclass
import cv2
import mediapipe as mp
import threading
import time
import ui
import camera_manager
import utils

@dataclass
class FaceLandmarkerState:
    godot_x: float = 0.0
    godot_y: float = 0.0
    estimated_z: float = 0.0
    image_x: int = 0
    image_y: int = 0

class FaceLandmarker:
    def __init__(self, udp_receiver_ip=None, udp_receiver_port=None, mp_landmarker_task_file=None, video_file=None, log_file=None, frame_delay_secs=None):
        self.udp_receiver_ip = udp_receiver_ip
        self.udp_receiver_port = udp_receiver_port

        self.video_file = video_file
        self.log_file = log_file
        self.frame_delay_secs = frame_delay_secs

        self.state = FaceLandmarkerState()
        self.ui_config = ui.UiConfig()
        
        if self.video_file:
            self.capture = cv2.VideoCapture(self.video_file)
        else:
            self.capture = None
            self.camera = camera_manager.CameraManager()
        
        self.stop_event = threading.Event()
    
        self.landmarker_options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=mp_landmarker_task_file),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.1
        )

    def run(self):
        if self.video_file:
            while not self.stop_event.is_set():
                ret, frame = self.capture.read()
                if not ret:
                    print("video ended or no frame available")
                    break
                start_time = time.time()
                self._process_frame(frame)
                exec_time_us = int((time.time() - start_time) * 1_000_000)

                with open(self.log_file, 'a') as f:
                    f.write(f"{exec_time_us}\n")

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
            
            self.capture.release()
            cv2.destroyAllWindows()
        else:
            self.camera.start()
            try:
                with mp.tasks.vision.FaceLandmarker.create_from_options(self.landmarker_options) as landmarker:
                    while not self.stop_event.is_set():
                        frame = self.camera.current_frame
                        if frame is None:
                            print("no frame available")
                            continue
                        
                        self._process_frame(frame, landmarker)

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
            finally:
                self.camera.stop()
                cv2.destroyAllWindows()

    def _process_frame(self, frame, landmarker=None):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        if not landmarker:
            print("no detector provided")
            return

        if self.video_file:    
            start_time = time.time()
            results = landmarker.detect(mp_image)
            exec_time_us = int((time.time() - start_time) * 1_000_000)
            with open(self.log_file, 'a') as f:
                f.write(f"{exec_time_us}\n")
        else:
            results = landmarker.detect(mp_image)

        if not results.face_landmarks:
            print("no face detected")
            return
        
        (eye_midpoint_x, eye_midpoint_y) = utils.extract_eye_midpoint_from_landmarks(results.face_landmarks[0], frame.shape)
        
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
