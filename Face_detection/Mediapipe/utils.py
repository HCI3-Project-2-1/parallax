def smooth_coordinates(new_x, new_y, new_z, prev_x, prev_y, prev_z, alpha):
    """Smooth the coordinates using exponential smoothing."""
    if prev_x is None or prev_y is None or prev_z is None:
        return new_x, new_y, new_z
    smoothed_x = alpha * new_x + (1 - alpha) * prev_x
    smoothed_y = alpha * new_y + (1 - alpha) * prev_y
    smoothed_z = alpha * new_z + (1 - alpha) * prev_z
    return smoothed_x, smoothed_y, smoothed_z

def estimate_distance(face_width_pixels, image_width, focal_length=615, face_width_cm=14):
    """Estimate the distance of the face from the camera."""
    face_width_pixels = max(1, face_width_pixels)  # Avoid division by zero
    distance = (face_width_cm * focal_length) / (face_width_pixels * 0.1)
    return distance
