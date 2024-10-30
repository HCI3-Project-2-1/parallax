#ifndef GDEXTENSION_REGISTER_TYPES_HPP
#define GDEXTENSION_REGISTER_TYPES_HPP

#include "camera_extension/camera_extension.hpp"
#include <gdextension_interface.h>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/defs.hpp>
#include <godot_cpp/godot.hpp>

using namespace godot;

void initialize_camera_extension_module(ModuleInitializationLevel p_level);
void uninitialize_camera_extension_module(ModuleInitializationLevel p_level);

#endif // GDEXTENSION_REGISTER_TYPES_HPP
