#include "opencv_camera.hpp"

using namespace godot;

void OpencvCamera::_bind_methods() {}

OpencvCamera::OpencvCamera() { time_passed = 0.0; }

OpencvCamera::~OpencvCamera() {}

void OpencvCamera::_process(double delta) {
  time_passed += delta;

  Vector2 new_position = Vector2(10.0 + (10.0 * sin(time_passed * 2.0)),
                                 10.0 + (10.0 * cos(time_passed * 1.5)));

  set_position(new_position);
}
