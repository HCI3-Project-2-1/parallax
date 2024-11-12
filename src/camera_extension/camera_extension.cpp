#include "camera_extension.hpp"

// TODO make this a relative path
const char *MODEL_PATH =
    "/home/pedro/uni/year_2/hci/project/parallax/godot_project/"
    "assets/face_detection_model.dat";
const char *HAAR_CASCADE_PATH =
    "/home/pedro/uni/year_2/hci/project/parallax/godot_project/"
    "assets/haarcascade_lefteye.xml";
const float DEFAULT_Z = 10.0;

// -1.0 for both to use default camera resolution
const int CAMERA_WIDTH = -1.0;
const int CAMERA_HEIGHT = -1.0;

// post-processing downscaling factor
const float INPUT_FRAME_SCALE_FACTOR = 1.0;

const int CAMERA_COORDS_SCALAR = 1;
const int NOSE_TIP_IDX = 30;

// between-frame-coords smoothing factor
const float ALPHA = 0.5;

using namespace godot;

void CameraExtension::_bind_methods() {}

CameraExtension::CameraExtension() {
  time_passed = 0.0;
  previousEyeScreenCoords = {0.0, 0.0};
  rawEyeScreenCoords = {0.0, 0.0};

  load_model();
  open_camera();

  godot::UtilityFunctions::print("CameraExtension instantiated");
}

CameraExtension::~CameraExtension() {
  this->capture.release();
  godot::UtilityFunctions::print("camera device released");
  godot::UtilityFunctions::print("CameraExtension destroyed");
}

void CameraExtension::load_model() {
  /*godot::UtilityFunctions::print("model path: ", MODEL_PATH);*/

  // TODO these dlib calls cause the object to be destroyed then re-created
  this->left_eye_detector = cv::CascadeClassifier(HAAR_CASCADE_PATH);
  godot::UtilityFunctions::print("instantiated face detector");
  this->pose_model = dlib::shape_predictor();
  godot::UtilityFunctions::print("instantiated pose model");

  try {
    dlib::deserialize(MODEL_PATH) >> this->pose_model;
  } catch (const dlib::serialization_error &e) {
    godot::UtilityFunctions::print("failed to load model: ", e.what());
  } catch (const std::exception &e) {
    godot::UtilityFunctions::print("general error: ", e.what());
  } catch (...) {
    godot::UtilityFunctions::print("unknown error");
  }

  godot::UtilityFunctions::print("loaded model");
}

void CameraExtension::open_camera() {
  this->capture = cv::VideoCapture();

  godot::UtilityFunctions::print("instantiated capture");

  if (!this->capture.open(0, cv::CAP_V4L2)) {
    godot::UtilityFunctions::print("failed to open camera device");
    return;
  }

  if (CAMERA_WIDTH != -1 && CAMERA_HEIGHT != -1) {
    this->capture.set(cv::CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH);
    this->capture.set(cv::CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT);

    godot::UtilityFunctions::print("set camera resolution to ", CAMERA_WIDTH,
                                   "x", CAMERA_HEIGHT);
  }
}

void CameraExtension::smooth_coordinates() {
  // negatives coords when no face is detected
  if (this->previousEyeScreenCoords.x < 0 ||
      this->previousEyeScreenCoords.y < 0) {
    this->smoothedEyeScreenCoords = this->rawEyeScreenCoords;
  } else {
    this->smoothedEyeScreenCoords = {
        ALPHA * this->rawEyeScreenCoords.x +
            (1 - ALPHA) * this->previousEyeScreenCoords.x,
        ALPHA * this->rawEyeScreenCoords.y +
            (1 - ALPHA) * this->previousEyeScreenCoords.y};
  }

  this->previousEyeScreenCoords = {this->smoothedEyeScreenCoords.x,
                                   this->smoothedEyeScreenCoords.y};
}

EyeScreenCoords CameraExtension::dlib_resolve_eye_coords() {
  this->capture >> this->frame;
  if (this->frame.empty()) {
    godot::UtilityFunctions::print("failed to read frame");
    return {-1.0, -1.0};
  }

  // cv::imshow("current frame", frame);
  // cv::waitKey(0);
  // cv::destroyWindow("current frame");

  if (INPUT_FRAME_SCALE_FACTOR != 1.0) {
    godot::UtilityFunctions::print("downscaling frame");
    cv::resize(this->frame, this->frame, cv::Size(), INPUT_FRAME_SCALE_FACTOR,
               INPUT_FRAME_SCALE_FACTOR);
  }

  // TODO is allocation of cv::Mats expensive ? or any other allocation in this
  // function ?
  cv::Mat gray;
  cv::cvtColor(this->frame, gray, cv::COLOR_BGR2GRAY);

  auto cimg = dlib::cv_image<dlib::bgr_pixel>(frame);

  auto startTime = std::chrono::high_resolution_clock::now();
  auto faces = this->face_detector(cimg);
  auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
                      std::chrono::high_resolution_clock::now() - startTime)
                      .count();
  godot::UtilityFunctions::print("face detector took ", duration, "ms");

  if (faces.empty()) {
    return {-1.0, -1.0};
  }

  this->face_rect = faces[0];
  this->has_detected_face = true;

  startTime = std::chrono::high_resolution_clock::now();
  dlib::full_object_detection shape = this->pose_model(cimg, this->face_rect);
  duration = std::chrono::duration_cast<std::chrono::milliseconds>(
                 std::chrono::high_resolution_clock::now() - startTime)
                 .count();
  godot::UtilityFunctions::print("pose model took ", duration, "ms");

  this->rawEyeScreenCoords = {(float)shape.part(NOSE_TIP_IDX).x(),
                              (float)shape.part(NOSE_TIP_IDX).y()};

  this->smooth_coordinates();

  int screenWidth = this->frame.cols;
  int screenHeight = this->frame.rows;

  // normalize the coordinates over the screen matrix (frame)
  // `* 2 - 1` scales the normalized value from [0, 1] to [-1, 1]
  float norm_x = (this->smoothedEyeScreenCoords.x / screenWidth) * 2 - 1;
  // invert the y axis since the screen coordinates have top-left origin
  float norm_y = -((this->smoothedEyeScreenCoords.y / screenHeight) * 2 - 1);

  return {norm_x, norm_y};
}

EyeScreenCoords CameraExtension::opencv_resolve_eye_coords() {
  this->capture >> this->frame;
  if (this->frame.empty()) {
    godot::UtilityFunctions::print("failed to read frame");
    return {-1.0, -1.0};
  }

  // TODO is allocation of cv::Rects expensive ?
  std::vector<cv::Rect> left_eye_rects;
  this->left_eye_detector.detectMultiScale(this->frame, left_eye_rects);

  if (left_eye_rects.empty()) {
    return {-1.0, -1.0};
  }

  cv::Rect left_eye_rect = left_eye_rects[0];

  this->rawEyeScreenCoords = {
      (float)left_eye_rect.x + (float)left_eye_rect.width / 2,
      (float)left_eye_rect.y + (float)left_eye_rect.height / 2};

  this->smooth_coordinates();

  int screenWidth = this->frame.cols;
  int screenHeight = this->frame.rows;

  // normalize the coordinates over the screen matrix (frame)
  // `* 2 - 1` scales the normalized value from [0, 1] to [-1, 1]
  // invert the y axis since the screen coordinates have top-left origin
  float norm_x = (this->smoothedEyeScreenCoords.x / screenWidth) * 2 - 1;
  float norm_y = -((this->smoothedEyeScreenCoords.y / screenHeight) * 2 - 1);

  return {norm_x, norm_y};
}

void CameraExtension::_process(double delta) {
  // this->time_passed += delta;
  // godot::UtilityFunctions::print("time passed: ", this->time_passed);

  auto startTime = std::chrono::high_resolution_clock::now();
  EyeScreenCoords newCoords = this->opencv_resolve_eye_coords();
  auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
                      std::chrono::high_resolution_clock::now() - startTime)
                      .count();

  // TODO robust error handling
  if (newCoords.x == -1.0 && newCoords.y == -1.0) {
    godot::UtilityFunctions::print("no faces detected");
    return;
  }

  godot::UtilityFunctions::print("eye coords computation took ", duration,
                                 "ms");

  /*godot::UtilityFunctions::print("newCoords: ", newCoords.x, " , ",*/
  /*                               newCoords.y);*/

  Vector3 new_position =
      Vector3(newCoords.x, newCoords.y, DEFAULT_Z) * CAMERA_COORDS_SCALAR;

  this->set_position(new_position);
}
