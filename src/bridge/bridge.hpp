#ifndef BRIDGE_HPP
#define BRIDGE_HPP

namespace bridge {
struct EyeScreenCoords {
  float x;
  float y;
};

class Bridge {
public:
  void push(EyeScreenCoords coords);
  EyeScreenCoords pop();
  bool is_empty() const;
};
} // namespace bridge
  //
#endif
