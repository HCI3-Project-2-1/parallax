from dataclasses import dataclass
import cv2

# `dataclass` denotes simple data containers
@dataclass
class UiConfig:
    show_overlay: bool = True
    frame_title: str = "Face Tracking"
    font: int = cv2.FONT_HERSHEY_DUPLEX
    font_scale: float = 0.75
    font_color: tuple = (50, 200, 50)
    font_thickness: int = 1
    circle_color: tuple = (0, 200, 0)
    circle_radius: int = 4

def draw_overlay(face_tracker, frame) -> None:
    """Render UI overlay on frame with current tracking state"""
    cv2.circle(frame, 
            (face_tracker.state.image_x, face_tracker.state.image_y), 
            face_tracker.ui_config.circle_radius, 
            face_tracker.ui_config.circle_color,
            -1)

    cv2.putText(frame, f"X: {face_tracker.state.image_x}, Y: {face_tracker.state.image_y}",
            (10, 30), face_tracker.ui_config.font, face_tracker.ui_config.font_scale, 
            face_tracker.ui_config.font_color, face_tracker.ui_config.font_thickness)

    cv2.putText(frame, "press 'o' to toggle overlays", (10, frame.shape[0] - 50),
            face_tracker.ui_config.font, face_tracker.ui_config.font_scale, 
            face_tracker.ui_config.font_color, face_tracker.ui_config.font_thickness)
    cv2.putText(frame, "press 'q' to quit", (10, frame.shape[0] - 30),
            face_tracker.ui_config.font, face_tracker.ui_config.font_scale, 
            face_tracker.ui_config.font_color, face_tracker.ui_config.font_thickness)