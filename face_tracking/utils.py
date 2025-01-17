import socket
import time

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_udp_data(ip, port, new_coords):
    """Send normalized coordinates to an arbitrary receiver via UDP."""
    x, y, z = new_coords
    # `time.time()` uses unix format, compatible with godot's `OS.get_ticks_msec()`
    message = f"{time.time()} {x:.4f} {y:.4f} {z:.4f}"
    try:
        socket.sendto(message.encode(), (ip, port))
    except Exception as e:
        print(f"udp send error: {e}")

def transform_landmark_coords(self, landmarks, image_dimensions):
    """Compute target screen coordinates from facial landmarks."""

    left_eye = landmarks[133]
    right_eye = landmarks[362]

    eye_midpoint_x = (left_eye.x + right_eye.x) / 2
    eye_midpoint_y = (left_eye.y + right_eye.y) / 2

    x = int(eye_midpoint_x * image_dimensions[1])
    y = int(eye_midpoint_y * image_dimensions[0])

    # transform from image coordinate system (top-left origin) 
    # to screen coordinate system (center origin)
    normalized_x = (x / image_dimensions[0]) * 2 - 1
    normalized_y = -((y / image_dimensions[1]) * 2 - 1)
    z_mean = (left_eye.z + right_eye.z) / 2

    self.state.image_x = x
    self.state.image_y = y

    self.state.x = normalized_x
    self.state.y = normalized_y
    self.state.z = z_mean

def extract_eye_midpoint_from_landmarks(landmarks, frame_dimensions):
    """Compute eye midpoint from detected face."""
    left_eye = landmarks[133]
    right_eye = landmarks[362]

    eye_midpoint_x = (left_eye.x + right_eye.x) / 2
    eye_midpoint_y = (left_eye.y + right_eye.y) / 2

    eye_midpoint_x = int(eye_midpoint_x * frame_dimensions[1])
    eye_midpoint_y = int(eye_midpoint_y * frame_dimensions[0])

    return (eye_midpoint_x, eye_midpoint_y)

def extract_eye_midpoint_from_detection(face_detection, frame_dimensions):
    """Compute eye midpoint from detected face."""
    left_eye_keypoint = face_detection.keypoints[0]
    right_eye_keypoint = face_detection.keypoints[1]

    eye_midpoint_x = (left_eye_keypoint.x + right_eye_keypoint.x) / 2
    eye_midpoint_y = (left_eye_keypoint.y + right_eye_keypoint.y) / 2

    eye_midpoint_x = int(eye_midpoint_x * frame_dimensions[1])
    eye_midpoint_y = int(eye_midpoint_y * frame_dimensions[0])

    return (eye_midpoint_x, eye_midpoint_y)

def transform_to_godot_coords(screen_x, screen_y, frame_dimensions):
    """Transform detected keypoint screen coordinates to Godot's coordinate system."""
    # transform from image coordinate system (top-left origin) 
    # to screen coordinate system (center origin)
    normalized_x = (screen_x / frame_dimensions[0]) * 2 - 1
    normalized_y = -((screen_y / frame_dimensions[1]) * 2 - 1)

    return (normalized_x, normalized_y)
