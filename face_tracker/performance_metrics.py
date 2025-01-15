import time
import psutil
import numpy as np

class PerformanceMetrics:
    def __init__(self):
        self.frame_count = 0
        self.start_time = time.time()
        self.detected_frames = 0
        self.errors = []
        self.x_coords = []
        self.y_coords = []
        self.cpu_usages = []
        self.memory_usages = []

    def update_fps(self):
        """Update frame count and calculate FPS."""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time <= 0.001:
            return 0.0
        return self.frame_count / elapsed_time

    def update_detection(self, detected):
        """Update the detection count for frames where a face is detected."""
        if detected:
            self.detected_frames += 1

    def calculate_detection_rate(self):
        """Calculate the percentage of frames with a face detected."""
        return (self.detected_frames / self.frame_count) * 100 if self.frame_count > 0 else 0

    def add_coordinates_for_jitter(self, x, y):
        """Store x and y coordinates for jitter calculation."""
        self.x_coords.append(x)
        self.y_coords.append(y)

    def calculate_jitter(self):
        """Calculate jitter (standard deviation) for x and y coordinates."""
        jitter_x = np.std(self.x_coords) if self.x_coords else 0
        jitter_y = np.std(self.y_coords) if self.y_coords else 0
        return jitter_x, jitter_y

    def update_cpu_usage(self):
        """Track the current CPU usage."""
        self.cpu_usages.append(psutil.cpu_percent())

    def calculate_average_cpu_usage(self):
        """Calculate the average CPU usage."""
        return sum(self.cpu_usages) / len(self.cpu_usages) if self.cpu_usages else 0

    def update_memory_usage(self):
        """Track the current memory usage."""
        memory_usage = psutil.Process().memory_info().rss
        self.memory_usages.append(memory_usage)

    def calculate_average_memory_usage(self):
        """Calculate the average memory usage."""
        return sum(self.memory_usages) / len(self.memory_usages) if self.memory_usages else 0

    def reset(self):
        """Reset all metrics."""
        self.frame_count = 0
        self.detected_frames = 0
        self.errors = []
        self.x_coords = []
        self.y_coords = []
        self.cpu_usages = []
        self.memory_usages = []
        self.start_time = time.time()
