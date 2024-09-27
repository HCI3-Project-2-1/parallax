#!/usr/bin/env python

# load godot-cpp binds environment 
env = SConscript("include/godot-cpp/SConstruct")

# append the source directory to the include path
env.Append(CPPPATH=["src/", "include/godot-cpp/include"])

if env["platform"] == "linux":
    env.ParseConfig("pkg-config --cflags --libs opencv4")

# lib binary output dir
godot_project_bin = "godot_project/bin"
library_name = "lib_opencv_camera_gdextension"

sources = Glob("src/opencv_camera/*.cpp") + Glob("src/vision/*.cpp") + ["src/register_types.cpp"]

if env["platform"] == "macos":
    library = env.SharedLibrary(
        target="{}/{}.{}.{}.framework/{}.{}.{}".format(
            godot_project_bin, library_name, env["platform"], env["target"], env["platform"], env["target"]
        ),
        source=sources,
    )
else:
    library = env.SharedLibrary(
        target="{}/{}{}{}".format(
            godot_project_bin, library_name, env["suffix"], env["SHLIBSUFFIX"]
        ),
        source=sources,
    )

Default(library)
