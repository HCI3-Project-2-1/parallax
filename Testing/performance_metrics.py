import time
import math
import numpy as np
import psutil  # To measure CPU and memory usage


class PerformanceMetrics:
    def __init__(self):
        self.frame_count = 0
        self.start_time = time.time()
        self.detected_frames = 0
        self.errors = []  # List to store the localization errors
        self.x_coords = []  # List to store X coordinates for jitter calculation
        self.y_coords = []  # List to store Y coordinates for jitter calculation

        # Initialize CPU and memory usage tracking
        self.cpu_usages = []
        self.memory_usages = []

    def update_fps(self):
        """Updates frame count and returns current FPS."""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time == 0:  # Avoid division by zero
            return 0
        fps = self.frame_count / elapsed_time
        return fps

    def update_detection(self, detected):
        """Updates detection frames count based on whether a face is detected."""
        if detected:
            self.detected_frames += 1

    def calculate_detection_rate(self):
        """Calculates the detection rate based on the number of detected frames."""
        if self.frame_count == 0:  # Avoid division by zero
            return 0
        detection_rate = (self.detected_frames / self.frame_count) * 100
        return detection_rate

    def add_localization_error(self, detected_x, detected_y, true_x, true_y):
        """Calculates and stores the Euclidean distance error for localization accuracy."""
        error = math.sqrt((detected_x - true_x) ** 2 + (detected_y - true_y) ** 2)
        self.errors.append(error)

    def calculate_average_error(self):
        """Calculates the average localization error."""
        if len(self.errors) == 0:
            return 0
        average_error = sum(self.errors) / len(self.errors)
        return average_error

    def add_coordinates_for_jitter(self, x, y):
        """Records the detected coordinates for jitter calculation."""
        self.x_coords.append(x)
        self.y_coords.append(y)

    def calculate_jitter(self):
        """Calculates jitter (standard deviation) for the detected coordinates."""
        if len(self.x_coords) == 0 or len(self.y_coords) == 0:
            return 0, 0

        # Convert lists to numpy arrays for standard deviation calculation
        x_array = np.array(self.x_coords)
        y_array = np.array(self.y_coords)

        # Calculate mean and standard deviation
        jitter_x = np.std(x_array)
        jitter_y = np.std(y_array)

        return jitter_x, jitter_y

    def update_cpu_usage(self):
        """Records the current CPU usage."""
        cpu_usage = psutil.cpu_percent()  # Get current CPU usage percentage
        self.cpu_usages.append(cpu_usage)

    def calculate_average_cpu_usage(self):
        """Calculates the average CPU usage over the execution."""
        if len(self.cpu_usages) == 0:
            return 0
        return sum(self.cpu_usages) / len(self.cpu_usages)

    def update_memory_usage(self):
        """Records the current memory usage."""
        memory_info = psutil.Process().memory_info()
        memory_usage = memory_info.rss  # Get memory usage in bytes
        self.memory_usages.append(memory_usage)

    def calculate_average_memory_usage(self):
        """Calculates the average memory usage over the execution."""
        if len(self.memory_usages) == 0:
            return 0
        return sum(self.memory_usages) / len(self.memory_usages)

    def reset(self):
        """Resets all metrics for a fresh calculation."""
        self.frame_count = 0
        self.detected_frames = 0
        self.errors = []
        self.x_coords = []
        self.y_coords = []
        self.cpu_usages = []
        self.memory_usages = []
        self.start_time = time.time()
