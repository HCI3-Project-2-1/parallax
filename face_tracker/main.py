from face_tracker import FaceTracker

UDP_RECEIVER_IP = "127.0.0.1"
UDP_RECEIVER_PORT = 6969
MP_LANDMARKER_TASK = "./face_landmarker.task"

def main():
    tracker = FaceTracker(UDP_RECEIVER_IP, UDP_RECEIVER_PORT, MP_LANDMARKER_TASK)
    try:
        tracker.run()
    except KeyboardInterrupt:
        tracker.stop()

if __name__ == "__main__":
    main()