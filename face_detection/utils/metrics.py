import time

# TODO is this optimal ?    
def update_metrics(shared_data, lock, start_time, interval):
    """Update FPS and packets per second."""
    current_time = time.time()
    elapsed = current_time - start_time
    if elapsed >= interval:
        with lock:
            shared_data["avg_fps"] = shared_data["frame_count"] / elapsed
            shared_data["frame_count"] = 0
        return current_time
    return start_time