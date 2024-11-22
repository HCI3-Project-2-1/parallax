import socket
import threading
import time

import cv2
import mediapipe as mp

from utils import smoothing, camera, ui, metrics, network, face_processor

UDP_IP = "127.0.0.1"
UDP_PORT = 6969

# downscale frame size for performance gains
SCALARS = [1.0, 0.66, 0.33]

TOGGLE_KALMAN_KEY = "k"
TOGGLE_OVERLAYS_KEY = "o"
CYCLE_FRAME_SCALE_FACTOR_KEY = "s"
QUIT_KEY = "q"

MP_LANDMARKER_TASK = "./models/face_landmarker.task"


lock = threading.Lock()
# TODO more robust shared data structure ?
shared_data = {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
    "image_x": 0,
    "image_y": 0,
    "use_kalman": False,
    "frame_scale_factor": 1.0,
    "frame_queue": [],
    "frame_count": 0,
    "avg_fps": 0.0
}

def main():
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("failed to open device camera")
        return

    stop_event = threading.Event()

    video_capture_thread = threading.Thread(target=camera.capture_frames, args=(shared_data, lock, stop_event, video_capture))
    video_capture_thread.start()

    render_overlays = True

    try:
        base_options = mp.tasks.BaseOptions(model_asset_path=MP_LANDMARKER_TASK)
        # TODO experiment with options
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False
        )

        with mp.tasks.vision.FaceLandmarker.create_from_options(options) as landmarker:
            start_time = time.time()
            update_metrics_interval_secs = 1.0

            while not stop_event.is_set():
                with lock:
                    if not shared_data["frame_queue"]:
                        continue
                    frame = shared_data["frame_queue"].pop()
                    shared_data["frame_count"] += 1

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                # detect landmarks synchronously
                try:
                    results = landmarker.detect(mp_image)
                    if results.face_landmarks:
                        face_landmarks = results.face_landmarks[0]
                        new_coords = face_processor.transform_face_landmarks(shared_data, lock, face_landmarks, frame.shape[1], frame.shape[0])
                        network.send_udp_data(UDP_IP, UDP_PORT, new_coords)
                except Exception as e:
                    print(f"landmarker error: {e}")

                start_time = metrics.update_metrics(shared_data, lock, start_time, update_metrics_interval_secs)
                
                ui.display_frame(shared_data, lock, frame, render_overlays)

                key = cv2.waitKey(1) & 0xFF
                if key == ord(TOGGLE_OVERLAYS_KEY):
                    render_overlays = not render_overlays
                if key == ord(TOGGLE_KALMAN_KEY):
                    with lock:
                        shared_data["use_kalman"] = not shared_data["use_kalman"]
                if key == ord(CYCLE_FRAME_SCALE_FACTOR_KEY):
                    with lock:
                        shared_data["scalar_index"] = (shared_data.get("scalar_index", 0) + 1) % len(SCALARS)
                        shared_data["frame_scale_factor"] = SCALARS[shared_data["scalar_index"]]
                elif key == ord(QUIT_KEY):
                    stop_event.set()
                    break

    except Exception as e:
        print(f"an error occurred: {e}")
    finally:
        # cleanup
        stop_event.set()
        video_capture_thread.join()
        video_capture.release()
        cv2.destroyAllWindows()
        socket.close()

        # TODO understand python locking mechanism
        with lock:
            print(f"final avg fps: {shared_data["avg_fps"]:.2f}")

if __name__ == "__main__":
    main()
