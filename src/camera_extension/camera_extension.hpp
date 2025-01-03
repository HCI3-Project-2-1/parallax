#ifndef CAMERA_EXTENSION_HPP
#define CAMERA_EXTENSION_HPP

#include <dlib/image_processing.h>
#include <dlib/image_processing/frontal_face_detector.h>
#include <dlib/opencv.h>
#include <godot_cpp/classes/camera3d.hpp>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/utility_functions.hpp>
#include <opencv2/opencv.hpp>

namespace godot {
struct EyeScreenCoords {
  float x;
  float y;
};

class CameraExtension : public Camera3D {
  GDCLASS(CameraExtension, Camera3D)

private:
  dlib::frontal_face_detector face_detector;
  cv::CascadeClassifier left_eye_detector;
  dlib::shape_predictor pose_model;
  cv::Mat frame;
  cv::VideoCapture capture;
  bool has_detected_face;
  dlib::rectangle face_rect;

  int iterations;
  double time_passed;
  EyeScreenCoords smoothedEyeScreenCoords, previousEyeScreenCoords,
      rawEyeScreenCoords, finalEyeScreenCoords;

protected:
  static void _bind_methods();

public:
  CameraExtension();
  ~CameraExtension();

  void load_model();

  void open_camera();

  void smooth_coordinates();

  EyeScreenCoords dlib_resolve_eye_coords();
  EyeScreenCoords opencv_resolve_eye_coords();

  void _process(double delta) override;
};

} // namespace godot

#endif
