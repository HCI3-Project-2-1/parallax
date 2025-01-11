#define WIN32_LEAN_AND_MEAN  
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <string>
#include <cmath>

#pragma comment(lib, "Ws2_32.lib")

// UDP setup
const std::string UDP_IP = "127.0.0.1";
const int UDP_PORT = 12345;
SOCKET sockfd;
sockaddr_in server_address;

const float alpha = 0.9f;  // Smoothing factor
float smoothed_left_x = -1, smoothed_left_y = -1;
float smoothed_right_x = -1, smoothed_right_y = -1;

bool eyes_found = false;  // Flag to indicate if eyes have been found
cv::Rect last_left_eye, last_right_eye, last_face;  // Store the last known eye positions
int frames_since_last_eye_detected = 0;  // Frame count since last successful detection
const int MAX_FRAMES_WITHOUT_EYE = 5;    // Allow a max of 5 frames without detection before stopping

const std::string FACE_CASCADE = "C:/Users/ilyas/Documents/face_tracker/models/haarcascade_frontalface_default.xml"; 
const std::string EYE_CASCADE = "C:/Users/ilyas/Documents/face_tracker/models/haarcascade_eye.xml";  

std::pair<float, float> smooth_coordinates(float center_x, float center_y, float smoothed_x, float smoothed_y, float alpha) {
    if (smoothed_x == -1 || smoothed_y == -1) {
        return {center_x, center_y};
    }
    float new_smoothed_x = alpha * center_x + (1 - alpha) * smoothed_x;
    float new_smoothed_y = alpha * center_y + (1 - alpha) * smoothed_y;
    return {new_smoothed_x, new_smoothed_y};
}

void send_coordinates(SOCKET sockfd, float left_x, float left_y, float right_x, float right_y) {
    std::string message = std::to_string(left_x) + "," + std::to_string(left_y) + "," + std::to_string(right_x) + "," + std::to_string(right_y);
    std::cerr << "Eye coordinates: " << message << std::endl;
    sendto(sockfd, message.c_str(), static_cast<int>(message.length()), 0, (sockaddr*)&server_address, sizeof(server_address));
}

// Calculate Euclidean distance
double calculate_distance(int x1, int y1, int x2, int y2) {
    return std::sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
}

// Find the two best eye candidates (closest pair)
std::pair<cv::Rect, cv::Rect> find_best_eye_pair(std::vector<cv::Rect>& eyes) {
    std::pair<cv::Rect, cv::Rect> best_pair;
    double best_distance = std::numeric_limits<double>::max();

    // Compare every pair of eyes to find the closest pair
    for (size_t i = 0; i < eyes.size(); ++i) {
        for (size_t j = i + 1; j < eyes.size(); ++j) {
            double distance = calculate_distance(
                eyes[i].x + eyes[i].width / 2, eyes[i].y + eyes[i].height / 2,
                eyes[j].x + eyes[j].width / 2, eyes[j].y + eyes[j].height / 2
            );
            // If the distance is better, select this pair
            if (distance > 50 && distance < 200 && distance < best_distance) {
                best_distance = distance;
                best_pair = {eyes[i], eyes[j]};
            }
        }
    }
    return best_pair;
}

int main() {
    // Initialize WinSock
    std::cerr << "Initializing WinSock..." << std::endl;
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "Error: Could not initialize WinSock" << std::endl;
        return -1;
    }

    // Create UDP socket
    std::cerr << "Creating UDP socket..." << std::endl;
    sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sockfd == INVALID_SOCKET) {
        std::cerr << "Error: Could not create socket" << std::endl;
        WSACleanup();
        return -1;
    }

    // Configure server address
    std::cerr << "Configuring server address..." << std::endl;
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(UDP_PORT);
    server_address.sin_addr.s_addr = inet_addr(UDP_IP.c_str());

    // Haar Cascade for face and eye detection
    cv::CascadeClassifier face_cascade;
    if (!face_cascade.load(FACE_CASCADE)) {
        std::cerr << "Error: Could not load face cascade classifier" << std::endl;
        return -1;
    }

    cv::CascadeClassifier eye_cascade;
    if (!eye_cascade.load(EYE_CASCADE)) {
        std::cerr << "Error: Could not load eye cascade classifier" << std::endl;
        return -1;
    }

    // Open webcam
    std::cerr << "Opening webcam..." << std::endl;
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open webcam" << std::endl;
        closesocket(sockfd);
        WSACleanup();
        return -1;
    } else {
        std::cerr << "Webcam opened successfully." << std::endl;
    }

    while (cap.isOpened()) {
        cv::Mat frame;
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "Error: Frame capture failed" << std::endl;
            break;
        }

        int h = frame.rows;
        int w = frame.cols;

        std::vector<cv::Rect> faces;
        face_cascade.detectMultiScale(frame, faces, 1.1, 10, 0, cv::Size(100, 100));  // Face detection

        if (faces.size() > 0) {
            cv::Rect face = faces[0];  // Use the first detected face
            last_face = face;  // Store the face
            cv::rectangle(frame, face, cv::Scalar(255, 0, 0), 2);  // Draw blue rectangle around the face

            // Detect eyes within the face ROI
            cv::Mat faceROI = frame(face);
            std::vector<cv::Rect> eyes;
            eye_cascade.detectMultiScale(faceROI, eyes, 1.1, 10, 0, cv::Size(30, 30));

            if (eyes.size() >= 2) {
                // Find the best pair of eyes based on their distance
                auto [left_eye, right_eye] = find_best_eye_pair(eyes);

                // Ensure the left eye is on the left side
                if (left_eye.x > right_eye.x) {
                    std::swap(left_eye, right_eye);
                }

                // Adjust eye positions
                left_eye.x += face.x;
                left_eye.y += face.y;
                right_eye.x += face.x;
                right_eye.y += face.y;

                // Update last known eye positions
                last_left_eye = left_eye;
                last_right_eye = right_eye;
                eyes_found = true;
                frames_since_last_eye_detected = 0;  // Reset frame counter

                // Get the center of the left and right eyes
                int left_eye_center_x = left_eye.x + left_eye.width / 2;
                int left_eye_center_y = left_eye.y + left_eye.height / 2;
                int right_eye_center_x = right_eye.x + right_eye.width / 2;
                int right_eye_center_y = right_eye.y + right_eye.height / 2;

                // Smooth coordinates for both eyes
                std::tie(smoothed_left_x, smoothed_left_y) = smooth_coordinates(left_eye_center_x, left_eye_center_y, smoothed_left_x, smoothed_left_y, alpha);
                std::tie(smoothed_right_x, smoothed_right_y) = smooth_coordinates(right_eye_center_x, right_eye_center_y, smoothed_right_x, smoothed_right_y, alpha);

                // Normalize coordinates to range -1 to 1
                float norm_left_x = (smoothed_left_x / w) * 2 - 1;
                float norm_left_y = -((smoothed_left_y / h) * 2 - 1);  // Invert Y-axis
                float norm_right_x = (smoothed_right_x / w) * 2 - 1;
                float norm_right_y = -((smoothed_right_y / h) * 2 - 1);  // Invert Y-axis

                // Send normalized eye coordinates via UDP
                send_coordinates(sockfd, norm_left_x, norm_left_y, norm_right_x, norm_right_y);

                // Draw red dots over the eye centers
                cv::circle(frame, cv::Point(left_eye_center_x, left_eye_center_y), 5, cv::Scalar(0, 0, 255), -1);
                cv::circle(frame, cv::Point(right_eye_center_x, right_eye_center_y), 5, cv::Scalar(0, 0, 255), -1);
            } else {
                // If no eyes are detected, count the frames
                if (frames_since_last_eye_detected < MAX_FRAMES_WITHOUT_EYE && eyes_found) {
                    frames_since_last_eye_detected++;

                    int left_eye_center_x = last_left_eye.x + last_left_eye.width / 2;
                    int left_eye_center_y = last_left_eye.y + last_left_eye.height / 2;
                    int right_eye_center_x = last_right_eye.x + last_right_eye.width / 2;
                    int right_eye_center_y = last_right_eye.y + last_right_eye.height / 2;

                    // Draw red dots over the last known eye centers
                    cv::circle(frame, cv::Point(left_eye_center_x, left_eye_center_y), 5, cv::Scalar(0, 0, 255), -1);
                    cv::circle(frame, cv::Point(right_eye_center_x, right_eye_center_y), 5, cv::Scalar(0, 0, 255), -1);
                } else {
                    eyes_found = false;  // If eyes haven't been detected for too long, stop drawing the dots
                }
            }
        } else {
            // If no face is detected, stop drawing everything
            eyes_found = false;
        }

        // Show the video 
        cv::imshow("Face and Eye Detection", frame);

        if (cv::waitKey(1) == 'q') break;
    }

    std::cerr << "Cleaning up resources..." << std::endl;
    cap.release();
    cv::destroyAllWindows();
    closesocket(sockfd);
    WSACleanup();

    std::cerr << "Program finished." << std::endl;
    return 0;
}
