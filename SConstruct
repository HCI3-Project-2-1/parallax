#!/usr/bin/env python

# load godot-cpp binds environment 
env = SConscript("include/godot-cpp/SConstruct")

# append the source directory to the include path
env.Append(CPPPATH=["src/", "include/godot-cpp/include/", "/usr/include/opencv4"])

env.Append(LIBPATH=["/usr/lib/"])
env.Append(LIBS=["opencv_core", "opencv_highgui", "opencv_videoio", "dlib", "lapack", "blas"])

# we need exceptions for dlib model loading
env.Append(CCFLAGS=["-fexceptions"])

# lib binary output dir
godot_project_bin = "godot_project/bin"
library_name = "lib_camera_extension"

sources = Glob("src/camera_extension/*.cpp") + ["src/register_types.cpp"]

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
