#ifndef OPENCV_CAMERA_HPP
#define OPENCV_CAMERA_HPP

#include <godot_cpp/classes/camera3d.hpp>
#include <godot_cpp/core/class_db.hpp>
#include <opencv2/core.hpp>

namespace godot {

class OpencvCamera : public Camera3D {
  GDCLASS(OpencvCamera, Camera3D)

private:
  double time_passed;

protected:
  static void _bind_methods();

public:
  OpencvCamera();
  ~OpencvCamera();

  void _process(double delta) override;
};

} // namespace godot

#endif
