import cv2

# used to estimate distance from face width in pixels
FOCAL_LENGTH_MM = 615
# avg adult face width in cm
FACE_WIDTH_CM = 14

def capture_frames(shared_data, lock, stop_event, capture):
    """Capture frames from the camera and enqueue them."""
    while not stop_event.is_set():
        result, frame = capture.read()
        if not result:
            print("failed to read frame from capture")
            stop_event.set()
            break

        frame_height, frame_width = frame.shape[:2]
        
        with lock:
            scale_factor = shared_data.get("frame_scale_factor", 1.0)
            frame_queue = shared_data["frame_queue"]

        scaled_width = int(frame_width * scale_factor)
        scaled_height = int(frame_height * scale_factor)

        frame = cv2.resize(frame, (scaled_width, scaled_height))

        with lock:
            frame_queue.append(frame)

def estimate_distance(face_width_pixels):
    """Estimate distance from face width in pixels."""
    face_width_pixels = max(1, face_width_pixels)
    distance = (FACE_WIDTH_CM * FOCAL_LENGTH_MM) / (face_width_pixels * 0.1)
    return distance