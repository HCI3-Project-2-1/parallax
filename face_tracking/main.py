import psutil
import threading
import time
from face_landmarker import FaceLandmarker
from face_detector import FaceDetector
import sys
import os

UDP_RECEIVER_IP = "127.0.0.1"
UDP_RECEIVER_PORT = 6969


#!!! Test_man video is kinda long so if you want to stop the video quickly just press ctrl +c.
# It takes a lot of time when you run it in landmarker mode.

#Give a valid videopath to test: --> C:/Example/parallax/perf_metrics/female_head_shake.ogx
SAMPLE_VIDEO_FILE = "../perf_metrics/female_head_shake.ogx"

# https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/FaceLandmarker
LANDMARKER_TASK_FILE = "./models/face_landmarker.task"
FACE_LANDMARKER_LOG_FILE = "../perf_metrics/logs/python_face_landmarker_log.txt"

# https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/FaceDetector
FACE_DETECTOR_FILE = "./models/blaze_face_short_range.tflite"
FACE_DETECTOR_LOG_FILE = "../perf_metrics/logs/python_face_detector_log.txt"

FRAME_DELAY_SECS = None

# Function to monitor CPU and memory usage and calculate averages
def monitor_system_usage(stop_event, results):
    cpu_usages = []
    memory_usages = []

    while not stop_event.is_set():
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB
        cpu_usages.append(cpu_usage)
        memory_usages.append(memory_usage)

    results["avg_cpu"] = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0
    results["avg_memory"] = sum(memory_usages) / len(memory_usages) if memory_usages else 0

def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "landmarker"
    perf_mode = len(sys.argv) > 2 and sys.argv[2] == "perf"
    video_file = SAMPLE_VIDEO_FILE if perf_mode else None

    stop_event = threading.Event()
    results = {}

    # Start the system monitoring thread
    monitor_thread = threading.Thread(target=monitor_system_usage, args=(stop_event, results))
    monitor_thread.start()

    try:
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
            print("Invalid model. Use 'landmarker' or 'detector'")
    finally:
        # Stop the monitoring thread
        stop_event.set()
        monitor_thread.join()

        # Print average CPU and memory usage
        print(f"Average CPU Usage: {results.get('avg_cpu', 0):.2f}%")
        print(f"Average Memory Usage: {results.get('avg_memory', 0):.2f} MB")

if __name__ == "__main__":
    main()
