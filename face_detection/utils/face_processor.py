import mediapipe as mp

from utils import smoothing, camera


kalman_x = smoothing.create_kalman_filter()
kalman_y = smoothing.create_kalman_filter()
kalman_z = smoothing.create_kalman_filter()

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

def transform_face_landmarks(shared_data, lock, face_landmarks, image_width, image_height):
    """Compute target screen coordinates from facial landmarks."""
    nose_tip = face_landmarks[1]
    left_cheek = face_landmarks[234]
    right_cheek = face_landmarks[454]

    left_eye = face_landmarks[133]
    right_eye = face_landmarks[362]

    eye_midpoint_x = (left_eye.x + right_eye.x) / 2
    eye_midpoint_y = (left_eye.y + right_eye.y) / 2

    x = int(eye_midpoint_x * image_width)
    y = int(eye_midpoint_y * image_height)
    
    face_width_pixels = abs(left_cheek.x - right_cheek.x) * image_width
    distance = camera.estimate_distance(face_width_pixels)
    # TODO experiment with values below
    z = (distance - 30) / 100

    # transform from image coordinate system (top-left origin) 
    # to screen coordinate system (center origin)
    normalized_x = (x / image_width) * 2 - 1
    normalized_y = -((y / image_height) * 2 - 1)

    with lock:
        use_kalman = shared_data["use_kalman"]

    if use_kalman:
        final_x = smoothing.update_kalman_filter(kalman_x, normalized_x, shared_data["x"], 0)
        final_y = smoothing.update_kalman_filter(kalman_y, normalized_y, shared_data["y"], 0)
        final_z = smoothing.update_kalman_filter(kalman_z, z, shared_data["z"], 0)
    else:
        final_x = normalized_x
        final_y = normalized_y
        final_z = z

    with lock:
        shared_data["x"] = final_x
        shared_data["y"] = final_y
        shared_data["z"] = final_z
        shared_data["image_x"] = x
        shared_data["image_y"] = y

    return (final_x, final_y, final_z)