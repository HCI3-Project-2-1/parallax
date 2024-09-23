#ifndef OPENCV_EXTENSION_HPP
#define OPENCV_EXTENSION_HPP

#include <godot_cpp/classes/sprite2d.hpp>

namespace godot {

class OpencvExtension : public Sprite2D {
  GDCLASS(OpencvExtension, Sprite2D)

private:
  double time_passed;

protected:
  static void _bind_methods();

public:
  OpencvExtension();
  ~OpencvExtension();

  void _process(double delta) override;
};

} // namespace godot

#endif
