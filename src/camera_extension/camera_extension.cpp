#include "camera_extension.hpp"

// TODO make this a relative path
const char *MODEL_PATH = "/home/pedro/uni/year_2/hci/project/godot_project/"
                         "assets/face_detection_model.dat";
const float DEFAULT_Z = 10.0;
const int NOSE_TIP_IDX = 30;

using namespace godot;

void CameraExtension::_bind_methods() {}

CameraExtension::CameraExtension() {
  time_passed = 0.0;
  alpha = 0.5;
  previousEyeScreenCoords = {0.0, 0.0};
  rawEyeScreenCoords = {0.0, 0.0};

  load_model();
  /*open_camera();*/
}

CameraExtension::~CameraExtension() {}

void CameraExtension::_process(double delta) {
  this->time_passed += delta;

  /*godot::UtilityFunctions::print("time passed: ", this->time_passed);*/

  /*EyeScreenCoords newCoords = this->resolve_eye_coords();*/
  EyeScreenCoords newCoords = {-1.0, -1.0};

  // negatives coords when failed to read frame or no face is detected
  if (newCoords.x < 0 || newCoords.y < 0) {
    return;
  }

  Vector3 new_position = Vector3(newCoords.x, newCoords.y, DEFAULT_Z);

  this->set_position(new_position);
}

void CameraExtension::load_model() {
  this->face_detector = dlib::get_frontal_face_detector();
  godot::UtilityFunctions::print("loaded face detector");
  this->pose_model = dlib::shape_predictor();
  godot::UtilityFunctions::print("loaded pose model");

  try {
    dlib::deserialize(MODEL_PATH) >> pose_model;
  } catch (dlib::serialization_error &e) {
    godot::UtilityFunctions::print("failed to load model: ", e.what());
  }
}

void CameraExtension::open_camera() {
  this->capture = cv::VideoCapture(0);
  if (!this->capture.isOpened()) {
    godot::UtilityFunctions::print("failed to open camera");
  }
}

void CameraExtension::smooth_coordinates() {
  // negatives coords when no face is detected
  if (previousEyeScreenCoords.x < 0 || previousEyeScreenCoords.y < 0) {
    this->smoothedEyeScreenCoords = this->rawEyeScreenCoords;
  } else {
    this->smoothedEyeScreenCoords = {
        this->alpha * this->rawEyeScreenCoords.x +
            (1 - this->alpha) * this->previousEyeScreenCoords.x,
        this->alpha * this->rawEyeScreenCoords.y +
            (1 - this->alpha) * this->previousEyeScreenCoords.y};
  }

  this->previousEyeScreenCoords = {smoothedEyeScreenCoords.x,
                                   smoothedEyeScreenCoords.y};
}

EyeScreenCoords CameraExtension::resolve_eye_coords() {
  this->capture >> this->frame;
  if (frame.empty()) {
    godot::UtilityFunctions::print("failed to read frame");
    return {-1.0, -1.0};
  }

  cv::Mat gray;
  cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

  dlib::cv_image<dlib::bgr_pixel> cimg(frame);

  std::vector<dlib::rectangle> faces = face_detector(cimg);

  if (faces.size() == 0) {
    std::cerr << "no faces detected" << std::endl;
    return {-1.0, -1.0};
  }

  dlib::rectangle face = faces[0];
  dlib::full_object_detection shape = this->pose_model(cimg, face);

  this->rawEyeScreenCoords = {(float)shape.part(NOSE_TIP_IDX).x(),
                              (float)shape.part(NOSE_TIP_IDX).y()};
  this->smooth_coordinates();

  int screenWidth = frame.cols;
  int screenHeight = frame.rows;

  // normalize the coordinates over the screen matrix (frame)
  // `* 2 - 1` scales the normalized value from [0, 1] to [-1, 1]
  float norm_x = (smoothedEyeScreenCoords.x / screenWidth) * 2 - 1;
  // invert the y axis since the screen coordinates have top-left origin
  float norm_y = -((smoothedEyeScreenCoords.y / screenHeight) * 2 - 1);

  return {norm_x, norm_y};
}
