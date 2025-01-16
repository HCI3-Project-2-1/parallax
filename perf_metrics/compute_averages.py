GDMP_LANDMARKER_LOG_FILE = "./logs/gdmp_landmarker_log.txt"
PYTHON_FACE_LANDMARKER_LOG_FILE = "./logs/python_face_landmarker_log.txt"
PYTHON_FACE_DETECTOR_LOG_FILE = "./logs/python_face_detector_log.txt"

def compute_file_average(filename):
    total = 0
    count = 0
    with open(filename, 'r') as f:
        for line in f:
            total += float(line.strip())
            count += 1

    print(f"frame count: {count}")

    return total / count if count > 0 else 0

gdmp_landmarker_avg = compute_file_average(GDMP_LANDMARKER_LOG_FILE)
python_face_landmarker_avg = compute_file_average(PYTHON_FACE_LANDMARKER_LOG_FILE)
python_face_detector_avg = compute_file_average(PYTHON_FACE_DETECTOR_LOG_FILE)

print(f"gdmp landmarker avg: {gdmp_landmarker_avg:.2f} µs")
print(f"python face landmarker avg: {python_face_landmarker_avg:.2f} µs")
print(f"python face detector avg: {python_face_detector_avg:.2f} µs")
