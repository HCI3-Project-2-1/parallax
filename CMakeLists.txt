cmake_minimum_required(VERSION 3.10)
project(face_tracker_dnn)

set(CMAKE_C_COMPILER "C:/msys64/mingw32/bin/gcc.exe")

set(CMAKE_CXX_COMPILER "C:/msys64/mingw32/bin/g++.exe")

set(CMAKE_CXX_STANDARD 17)


find_package(OpenCV REQUIRED)


add_executable(face_tracker_dnn src/face_tracker_dnn.cpp)


target_link_libraries(face_tracker_dnn ${OpenCV_LIBS})


