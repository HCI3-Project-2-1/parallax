from face_landmarker import FaceLandmarker
from face_detector import FaceDetector
import sys
import os

UDP_RECEIVER_IP = "127.0.0.1"
UDP_RECEIVER_PORT = 6969

SAMPLE_VIDEO_FILE = "../perf_metrics/female_head_shake.ogx"

# https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/FaceLandmarker
LANDMARKER_TASK_FILE = "./models/face_landmarker.task"
FACE_LANDMARKER_LOG_FILE = "../perf_metrics/logs/python_face_landmarker_log.txt"

# https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/FaceDetector
FACE_DETECTOR_FILE = "./models/blaze_face_short_range.tflite"
FACE_DETECTOR_LOG_FILE = "../perf_metrics/logs/python_face_detector_log.txt"

FRAME_DELAY_SECS = None

def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "landmarker"
    perf_mode = len(sys.argv) > 2 and sys.argv[2] == "perf"
    video_file = SAMPLE_VIDEO_FILE if perf_mode else None
    
    if model == "landmarker":
        if FACE_LANDMARKER_LOG_FILE and os.path.exists(FACE_LANDMARKER_LOG_FILE):
                os.remove(FACE_LANDMARKER_LOG_FILE)
        landmarker = FaceLandmarker(UDP_RECEIVER_IP, UDP_RECEIVER_PORT, LANDMARKER_TASK_FILE, video_file, FACE_LANDMARKER_LOG_FILE, FRAME_DELAY_SECS)
        try:
            landmarker.run()
        except KeyboardInterrupt:
            landmarker.stop()
    elif model == "detector":
        if FACE_DETECTOR_LOG_FILE and os.path.exists(FACE_DETECTOR_LOG_FILE):
                os.remove(FACE_DETECTOR_LOG_FILE)
        detector = FaceDetector(UDP_RECEIVER_IP, UDP_RECEIVER_PORT, FACE_DETECTOR_FILE, video_file, FACE_DETECTOR_LOG_FILE, FRAME_DELAY_SECS)
        try:
            detector.run()
        except KeyboardInterrupt:
            detector.stop()
    else:
        print("invalid model. use 'landmarker' or 'detector'")

if __name__ == "__main__":
    main()
