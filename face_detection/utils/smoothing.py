import cv2
import numpy as np

# TODO is leveraging numpy measurably faster ? 
# https://en.wikipedia.org/wiki/Exponential_smoothing
def exponential_smoothing(series, alpha):
    result = [series[0]]
    for n in range(1, len(series)):
        result.append(alpha * series[n] + (1 - alpha) * result[n-1])
    return result

# TODO understand the parameters
def create_kalman_filter(state_dim=2, measure_dim=1, process_noise=0.03):
    """
    Create and configure a Kalman filter.

    Args:
        state_dim (int): Dimension of the state vector.
        measure_dim (int): Dimension of the measurement vector.
        process_noise (float): Scaling factor for process noise covariance.

    Returns:
        cv2.KalmanFilter: Configured Kalman filter instance.
    """
    kalman = cv2.KalmanFilter(state_dim, measure_dim)
    kalman.measurementMatrix = np.eye(measure_dim, state_dim, dtype=np.float32)
    kalman.transitionMatrix = np.array([[1, 1], [0, 1]], dtype=np.float32)
    kalman.processNoiseCov = np.eye(state_dim, dtype=np.float32) * process_noise
    kalman.errorCovPre = np.eye(state_dim, dtype=np.float32)
    return kalman

def update_kalman_filter(kalman_filter, measurement, filtered_value, norm_value):
    """
    Perform Kalman filter update: initialization, prediction, and correction.

    Args:
        kalman_filter (cv2.KalmanFilter): The Kalman filter to update.
        measurement (float): The current measurement value.
        filtered_value (float): The previously filtered value (None if uninitialized).
        norm_value (float): The normalized value to initialize if needed.

    Returns:
        float: The updated filtered value.
    """
    if filtered_value is None:
        kalman_filter.statePre = np.array([[norm_value], [0]], dtype=np.float32)

    kalman_filter.predict()

    kalman_filter.correct(np.array([[np.float32(measurement)]]))

    return kalman_filter.statePost[0][0]
