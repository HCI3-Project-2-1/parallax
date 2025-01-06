import socket

# used to estimate distance from face width in pixels
FOCAL_LENGTH_MM = 615
# avg adult face width in cm
FACE_WIDTH_CM = 14.0

def estimate_distance(face_width_pixels: float) -> float:
    """Estimate distance from face width in pixels."""
    face_width_pixels = max(1, face_width_pixels)
    # TODO is this dumb ?
    distance = (FACE_WIDTH_CM * FOCAL_LENGTH_MM) / (face_width_pixels * 0.1)
    return distance

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_udp_data(ip, port, new_coords):
    """Send normalized coordinates to an arbitrary receiver via UDP."""
    x, y, z = new_coords
    message = f"{x:.4f} {y:.4f} {z:.4f}"
    try:
        socket.sendto(message.encode(), (ip, port))
    except Exception as e:
        print(f"udp send error: {e}")

def transform_landmark_coords(self, landmarks, image_dimensions):
    """Compute target screen coordinates from facial landmarks."""
    nose_tip = landmarks[1]
    left_cheek = landmarks[234]
    right_cheek = landmarks[454]

    left_eye = landmarks[133]
    right_eye = landmarks[362]

    eye_midpoint_x = (left_eye.x + right_eye.x) / 2
    eye_midpoint_y = (left_eye.y + right_eye.y) / 2

    x = int(eye_midpoint_x * image_dimensions[1])
    y = int(eye_midpoint_y * image_dimensions[0])
    
    face_width_pixels = abs(left_cheek.x - right_cheek.x) * image_dimensions[0]
    distance = estimate_distance(face_width_pixels)
    # TODO experiment with values below
    z = (distance - 30) / 100

    # transform from image coordinate system (top-left origin) 
    # to screen coordinate system (center origin)
    normalized_x = (x / image_dimensions[0]) * 2 - 1
    normalized_y = -((y / image_dimensions[1]) * 2 - 1)

    if self.state.use_kalman:
        final_x = normalized_x  # TODO: implement Kalman filter
        final_y = normalized_y  # TODO: implement Kalman filter
        final_z = z            # TODO: implement Kalman filter
    else:
        final_x = normalized_x
        final_y = normalized_y
        final_z = z

    self.state.image_x = x
    self.state.image_y = y

    self.state.x = final_x
    self.state.y = final_y
    self.state.z = final_z