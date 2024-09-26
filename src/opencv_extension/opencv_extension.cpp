#include "opencv_extension.hpp"
#include <godot_cpp/core/class_db.hpp>
#include <opencv2/core.hpp>

using namespace godot;

void OpencvExtension::_bind_methods() {}

OpencvExtension::OpencvExtension() { time_passed = 0.0; }

OpencvExtension::~OpencvExtension() {}

void OpencvExtension::_process(double delta) {
  time_passed += delta;

  Vector2 new_position = Vector2(10.0 + (10.0 * sin(time_passed * 2.0)),
                                 10.0 + (10.0 * cos(time_passed * 1.5)));

  set_position(new_position);
}
