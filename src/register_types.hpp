#ifndef GDEXTENSION_REGISTER_TYPES_HPP
#define GDEXTENSION_REGISTER_TYPES_HPP

#include <godot_cpp/core/class_db.hpp>

using namespace godot;

void initialize_opencv_camera_module(ModuleInitializationLevel p_level);
void uninitialize_opencv_camera_module(ModuleInitializationLevel p_level);

#endif // GDEXTENSION_REGISTER_TYPES_HPP
