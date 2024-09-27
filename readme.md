# Godot C++ Extension Project

## Description
This project is a **Godot extension** written in **C++** using **Godot's GDExtension C++ API**. Includes logic for integrating and leveraging OpenCV. We use **SCons** as the build system.

## Prerequisites
- **Godot 4.3**
- **OpenCV 4.10** 
- **SCons** (build system)
- **Python 3.x**
- **C++ Compiler** (GCC, Clang, etc.)

### Install SCons
Use an OS specific package manager or `pip install scons`.


### Clone this repo
```bash
git clone https://github.com/HCI3-Project-2-1/parallax.git
cd parallax
```

### Generate C++ Godot bindings
```bash
cd include/godot-cpp
godot --dump-extension-api
scons platform=<your_platform> generate_bindings=yes custom_api_file=extension_api.json
cd ../..
```

### Compile the extension to `/godot_project/bin`
```bash
scons platform=<your_platform>
```
