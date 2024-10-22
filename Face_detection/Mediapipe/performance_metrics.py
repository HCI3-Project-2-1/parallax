import time
from timeit import default_timer as timer

class PerformanceMetrics:
    def __init__(self):
        self.show_metrics = False
        self.fps = 0
        self.udp_packets_per_sec = 0
        self.frame_count = 0
        self.start_time = timer()
        self.last_udp_count_time = time.time()
        self.current_udp_packets_per_sec = 0

    def toggle_metrics_display(self):
        self.show_metrics = not self.show_metrics

    def update_fps(self):
        elapsed_time = timer() - self.start_time
        self.fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0

    def reset_fps(self):
        self.frame_count = 0
        self.start_time = timer()

    def update_udp_packets(self, count):
        self.current_udp_packets_per_sec = count

    def reset_udp_packets(self):
        self.current_udp_packets_per_sec = 0
