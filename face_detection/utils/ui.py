import cv2

ui_config = {
    "frame_title": "Face Tracking",
    "font": cv2.FONT_HERSHEY_DUPLEX,
    "font_scale": 0.5,
    "font_color": (150, 50, 0),
    "thickness": 1,
    "circle_color": (0, 255, 0),
    "circle_radius": 4,
}

# Initialize window with NORMAL flag
cv2.namedWindow(ui_config["frame_title"], cv2.WINDOW_NORMAL)

def display_frame(shared_data, lock, frame, render_overlays=True):
    """Display the frame with annotations."""
    if not render_overlays:
        cv2.imshow("Face Tracking", frame)
        return

    with lock:
        x = shared_data["x"]
        y = shared_data["y"]
        z = shared_data["z"]
        image_x = shared_data["image_x"]
        image_y = shared_data["image_y"]
        use_kalman = shared_data["use_kalman"]
        avg_fps = shared_data["avg_fps"]

    cv2.circle(frame, (int(image_x), int(image_y)), ui_config["circle_radius"], ui_config["circle_color"], -1)

    cv2.putText(frame, f"{avg_fps:.2f}fps", (10, 30),
                ui_config["font"], ui_config["font_scale"], ui_config["font_color"], ui_config["thickness"])
    cv2.putText(frame, f"X: {x:.4f}, Y: {y:.4f}, Z: {z:.4f}",
            (10, 60), ui_config["font"], ui_config["font_scale"], ui_config["font_color"], ui_config["thickness"])
    cv2.putText(frame, "kalman filter: " + ("ON" if use_kalman else "OFF"), (10, 90),
                ui_config["font"], ui_config["font_scale"], ui_config["font_color"], ui_config["thickness"])
    
    cv2.putText(frame, "press 'k' to toggle kalman filter", (10, 360),
                ui_config["font"], ui_config["font_scale"], ui_config["font_color"], ui_config["thickness"])
    cv2.putText(frame, "press 'o' to toggle overlays", (10, 390),
                ui_config["font"], ui_config["font_scale"], ui_config["font_color"], ui_config["thickness"])
    cv2.putText(frame, "press 's' to cycle frame scale", (10, 420),
                ui_config["font"], ui_config["font_scale"], ui_config["font_color"], ui_config["thickness"])
    cv2.putText(frame, "press 'q' to quit", (10, 450),
                ui_config["font"], ui_config["font_scale"], ui_config["font_color"], ui_config["thickness"])

    cv2.imshow(ui_config["frame_title"], frame)