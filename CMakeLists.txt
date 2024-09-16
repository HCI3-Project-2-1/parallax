cmake_minimum_required(VERSION 3.30.3)

project(parallax)

set(CMAKE_CXX_STANDARD 23)
# generate compile_commands.json
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(ROOT_DIR "/home/pedro/uni/year_2/hci/project") 

include_directories(
  ${ROOT_DIR}/include 
  ${ROOT_DIR}/include/godot-cpp/include 
  ${ROOT_DIR}/include/godot-cpp/gen/include 
  ${ROOT_DIR}/include/godot-cpp/gdextension
)

add_executable(parallax ${ROOT_DIR}/src/main.cpp ${ROOT_DIR}/src/bridge/bridge.cpp ${ROOT_DIR}/src/engine/engine.cpp ${ROOT_DIR}/src/vision/vision.cpp)

target_link_libraries(parallax ${ROOT_DIR}/lib/libgodot-cpp.linux.template_debug.x86_64.a)
