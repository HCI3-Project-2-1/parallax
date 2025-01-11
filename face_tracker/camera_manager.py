import cv2
import threading

class CameraManager:
    def __init__(self, camera_id: int = 0):
        self.capture = cv2.VideoCapture(camera_id)
        self.frame_ready = threading.Event()
        self.current_frame = None
        self._stop_event = threading.Event()

    def start(self):
        if not self.capture.isOpened():
            raise RuntimeError("failed to open camera")
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def _capture_frames(self):
        while not self._stop_event.is_set():
            ret, frame = self.capture.read()
            if ret:
                self.current_frame = frame
                self.frame_ready.set()

    def stop(self):
        self._stop_event.set()
        if self.capture_thread:
            self.capture_thread.join()
        self.capture.release()