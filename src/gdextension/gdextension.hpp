#ifndef GDEXTENSION_HPP
#define GDEXTENSION_HPP

#include <godot_cpp/classes/sprite2d.hpp>

namespace godot {

class GDExtension : public Sprite2D {
  GDCLASS(GDExtension, Sprite2D)

private:
  double time_passed;

protected:
  static void _bind_methods();

public:
  GDExtension();
  ~GDExtension();

  void _process(double delta) override;
};

} // namespace godot

#endif
