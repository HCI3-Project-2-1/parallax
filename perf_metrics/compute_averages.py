GDMP_LANDMARKER_LOG_FILE = "./logs/gdmp_landmarker_log.txt"
PYTHON_FACE_LANDMARKER_LOG_FILE = "./logs/python_face_landmarker_log.txt"
PYTHON_FACE_DETECTOR_LOG_FILE = "./logs/python_face_detector_log.txt"
UDP_TRANSMISSION_TIMES_LOG_FILE = "./logs/udp_transmission_times_log.txt"

def compute_file_metrics(filename):
    total = 0.0
    count = 0
    mn = float('inf')
    mx = float('-inf')
    with open(filename, 'r') as f:
        for line in f:
            value = float(line.strip())
            total += value
            count += 1
            if value < mn:
                mn = value
            if value > mx:
                mx = value
    avg = total / count if count > 0 else 0
    mn = mn if count > 0 else 0
    mx = mx if count > 0 else 0
    print(f"frame count: {count}")
    return avg, mn, mx

gdmp_landmarker_avg, gdmp_landmarker_min, gdmp_landmarker_max = compute_file_metrics(GDMP_LANDMARKER_LOG_FILE)
python_face_landmarker_avg, python_face_landmarker_min, python_face_landmarker_max = compute_file_metrics(PYTHON_FACE_LANDMARKER_LOG_FILE)
python_face_detector_avg, python_face_detector_min, python_face_detector_max = compute_file_metrics(PYTHON_FACE_DETECTOR_LOG_FILE)
udp_transmission_avg, udp_transmission_min, udp_transmission_max = compute_file_metrics(UDP_TRANSMISSION_TIMES_LOG_FILE)

print(f"gdmp landmarker avg: {gdmp_landmarker_avg:.2f} µs, min: {gdmp_landmarker_min:.2f} µs, max: {gdmp_landmarker_max:.2f} µs")
print(f"python face landmarker avg: {python_face_landmarker_avg:.2f} µs, min: {python_face_landmarker_min:.2f} µs, max: {python_face_landmarker_max:.2f} µs")
print(f"python face detector avg: {python_face_detector_avg:.2f} µs, min: {python_face_detector_min:.2f} µs, max: {python_face_detector_max:.2f} µs")
print(f"udp transmission avg: {udp_transmission_avg:.2f} µs, min: {udp_transmission_min:.2f} µs, max: {udp_transmission_max:.2f} µs")
