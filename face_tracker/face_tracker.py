from dataclasses import dataclass
import cv2
import mediapipe as mp
import threading
import time
import ui
import camera_manager
import utils

@dataclass
class FaceTrackerState:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    image_x: int = 0
    image_y: int = 0
    use_kalman: bool = False

class FaceTracker:
    def __init__(self, udp_receiver_ip=None, udp_receiver_port=None, mp_landmarker_task=None):
        self.udp_receiver_ip = udp_receiver_ip
        self.udp_receiver_port = udp_receiver_port
        self.mp_landmarker_task = mp_landmarker_task
        
        self.state = FaceTrackerState()
        self.ui_config = ui.UiConfig()
        self.camera = camera_manager.CameraManager()
        self.stop_event = threading.Event()
        self._setup_mediapipe()

    def _setup_mediapipe(self):
        base_options = mp.tasks.BaseOptions(
            model_asset_path=self.mp_landmarker_task)
        self.options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.1
        )

    def run(self):
        self.camera.start()
        try:
            with mp.tasks.vision.FaceLandmarker.create_from_options(
                self.options) as landmarker:
                while not self.stop_event.is_set():
                    frame = self.camera.current_frame
                    if frame is None:
                        print("no frame available")
                        continue

                    start_time = time.time()        
                    self._process_frame(frame, landmarker)
                    self.state.avg_fps = 1.0 / (time.time() - start_time)

                    if self.ui_config.show_overlay:
                        ui.draw_overlay(self, frame)

                    cv2.imshow(self.ui_config.frame_title, frame)

                    if self.udp_receiver_ip and self.udp_receiver_port:
                        utils.send_udp_data(self.udp_receiver_ip, self.udp_receiver_port, (self.state.x, self.state.y, self.state.z))
                    
                    # bit-wise AND with 0xFF to extract ASCII value from ord
                    key = cv2.waitKey(1) & 0xFF
                    if key != 255:
                        self.handle_key_event(chr(key))
        finally:
            self.camera.stop()

    def _process_frame(self, frame, landmarker):        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        results = landmarker.detect(mp_image)
        
        if results.face_landmarks:
            utils.transform_landmark_coords(self, results.face_landmarks[0], frame.shape[:2])    
        else:
            None
            # print("no face detected")
    
    def handle_key_event(self, key: str):
        if key == 'k':
            self.state.use_kalman = not self.state.use_kalman
        elif key == 'o':
            self.ui_config.show_overlay = not self.ui_config.show_overlay
        elif key == 'q':
            self.stop()

    def stop(self):
        self.stop_event.set()
        self.camera.stop()
        cv2.destroyAllWindows()