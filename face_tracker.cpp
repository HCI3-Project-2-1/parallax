// face_tracker.cpp

#include <iostream>
#include <opencv2/opencv.hpp>
#include <dlib/image_processing.h>
#include <dlib/image_processing/frontal_face_detector.h>
#include <dlib/opencv.h>

// Per la comunicazione UDP
#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib,"ws2_32.lib")
    typedef int socklen_t;
#else
    #include <sys/socket.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #include <netinet/in.h>
    #include <sys/types.h>
#endif

// Costanti
const char* UDP_IP = "127.0.0.1";  // Godot in ascolto su localhost
const int UDP_PORT = 12354;
const float ALPHA = 0.3f;  // Fattore di smoothing per il filtro passa-basso

void smooth_coordinates(float new_x, float new_y, float& prev_x, float& prev_y, float alpha, float& smoothed_x, float& smoothed_y) {
    if (prev_x < 0 || prev_y < 0) {
        smoothed_x = new_x;
        smoothed_y = new_y;
    } else {
        smoothed_x = alpha * new_x + (1 - alpha) * prev_x;
        smoothed_y = alpha * new_y + (1 - alpha) * prev_y;
    }
    prev_x = smoothed_x;
    prev_y = smoothed_y;
}

void send_coordinates(int sockfd, float x, float y, struct sockaddr_in& server_addr) {
    char message[50];
    snprintf(message, sizeof(message), "%.4f,%.4f", x, y);
    #ifdef _WIN32
        sendto(sockfd, message, static_cast<int>(strlen(message)), 0, reinterpret_cast<const sockaddr*>(&server_addr), sizeof(server_addr));
    #else
        sendto(sockfd, message, strlen(message), 0, reinterpret_cast<const sockaddr*>(&server_addr), sizeof(server_addr));
    #endif
}

int main() {
    // Inizializzazione del socket UDP
    #ifdef _WIN32
        WSADATA wsa;
        WSAStartup(MAKEWORD(2,2),&wsa);
    #endif

    int sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sockfd < 0) {
        std::cerr << "Errore: impossibile creare il socket." << std::endl;
        return -1;
    }

    struct sockaddr_in server_addr;
    std::memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(UDP_PORT);
    #ifdef _WIN32
        server_addr.sin_addr.S_un.S_addr = inet_addr(UDP_IP);
    #else
        server_addr.sin_addr.s_addr = inet_addr(UDP_IP);
    #endif

    // Inizializzazione delle variabili
    float smoothed_x = -1.0f, smoothed_y = -1.0f;
    float prev_x = -1.0f, prev_y = -1.0f;

    // Carica il rilevatore di volti e il predittore di punti caratteristici
    dlib::frontal_face_detector detector = dlib::get_frontal_face_detector();
    dlib::shape_predictor pose_model;
    try {
        dlib::deserialize("/Users/matteo/Desktop/shape_predictor_68_face_landmarks.dat") >> pose_model;
    } catch (const std::exception& e) {
        std::cerr << "Errore nel caricamento del modello dei punti caratteristici: " << e.what() << std::endl;
        return -1;
    }

    // Avvia la cattura video
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "Errore: impossibile aprire la webcam." << std::endl;
        return -1;
    }

    // Variabili per la misurazione delle prestazioni
    int frame_count = 0;
    auto start_time = std::chrono::high_resolution_clock::now();

    try {
        while (true) {
            cv::Mat frame;
            cap >> frame;
            if (frame.empty()) {
                std::cerr << "Errore: impossibile leggere il frame." << std::endl;
                break;
            }

            // Converti l'immagine in scala di grigi
            cv::Mat gray;
            cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

            // Converti l'immagine OpenCV in Dlib
            dlib::cv_image<dlib::bgr_pixel> cimg(frame);

            // Rileva i volti
            std::vector<dlib::rectangle> faces = detector(cimg);

            if (faces.size() > 0) {
                // Prendi il primo volto rilevato
                dlib::rectangle face = faces[0];

                // Rileva i punti caratteristici
                dlib::full_object_detection shape = pose_model(cimg, face);

                // Ottieni le coordinate del punto desiderato (es. punta del naso)
                // Indice 30 è la punta del naso nel modello a 68 punti
                int idx_nose_tip = 30;
                float x = shape.part(idx_nose_tip).x();
                float y = shape.part(idx_nose_tip).y();

                // Esegui lo smoothing delle coordinate
                float smoothed_x, smoothed_y;
                smooth_coordinates(x, y, prev_x, prev_y, ALPHA, smoothed_x, smoothed_y);

                // Normalizza le coordinate nell'intervallo -1 a 1
                int w = frame.cols;
                int h = frame.rows;
                float norm_x = (smoothed_x / w) * 2 - 1;
                float norm_y = -((smoothed_y / h) * 2 - 1);  // Inverti l'asse Y

                // Invia le coordinate normalizzate a Godot tramite UDP
                send_coordinates(sockfd, norm_x, norm_y, server_addr);

                // Disegna i punti caratteristici sul frame
                for (int i = 0; i < shape.num_parts(); i++) {
                    cv::circle(frame, cv::Point(shape.part(i).x(), shape.part(i).y()), 2, cv::Scalar(0, 255, 0), -1);
                }

                // Evidenzia il punto utilizzato (punta del naso)
                cv::circle(frame, cv::Point(smoothed_x, smoothed_y), 5, cv::Scalar(255, 0, 0), -1);
                cv::putText(frame, "(" + std::to_string(norm_x).substr(0, 5) + ", " + std::to_string(norm_y).substr(0, 5) + ")",
                            cv::Point(x + 10, y - 10), cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(255, 0, 0), 1);
            }

            // Misurazione delle prestazioni
            frame_count++;
            auto now = std::chrono::high_resolution_clock::now();
            double elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count() / 1000.0;
            double fps = frame_count / elapsed_time;
            cv::putText(frame, "FPS: " + std::to_string(fps).substr(0, 5),
                        cv::Point(10, 30), cv::FONT_HERSHEY_SIMPLEX, 0.7,
                        cv::Scalar(0, 255, 255), 2);

            // Mostra il frame
            cv::imshow("Face Tracking", frame);

            if (cv::waitKey(1) == 'q') {
                break;
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Si è verificato un errore: " << e.what() << std::endl;
    }

    // Rilascia le risorse
    cap.release();
    cv::destroyAllWindows();
    #ifdef _WIN32
        closesocket(sockfd);
        WSACleanup();
    #else
        close(sockfd);
    #endif

    return 0;
}
