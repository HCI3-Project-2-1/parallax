# Godot C++ Extension Project

## Description
This project is a **Godot extension** written in **C++** using **Godot's GDExtension API**. It includes logic for integrating OpenCV functionalities. The project uses **SCons** as the build system.

## Prerequisites
- **Godot 4.x**
- **SCons** (build system)
- **Python 3.x**
- **Godot C++ bindings** (in `godot-cpp`)
- **C++ Compiler** (GCC, Clang, etc.)

### Install SCons
Use an OS specific package manager or `pip install scons`.


### Clone this repo
```bash
git clone https://github.com/HCI3-Project-2-1/parallax.git
cd paralax
```

### Generate C++ Godot bindings
```bash
cd include/godot-cpp
scons platform=<your_platform> generate_bindings=yes
cd ..
```

### Compile the extension to `godot_project/bin`
```bash
scons platform=<your_platform>
```
