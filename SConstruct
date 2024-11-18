#!/usr/bin/env python

env = SConscript("include/godot-cpp/SConstruct")

env.Append(CPPPATH=["src/", "include/godot-cpp/include/"])

if env["platform"] == "linux":
    env.Append(CPPPATH=["/usr/include/opencv4"])
    env.Append(LIBPATH=["/usr/lib/"])
    env.Append(LIBS=["opencv_core", "opencv_highgui", "opencv_videoio", "dlib", "lapack", "blas"])

elif env["platform"] == "macos":
    env.Append(CPPPATH=["/usr/local/include/opencv4"])
    env.Append(LIBPATH=["/usr/local/lib/"])
    env.Append(LIBS=["opencv_core", "opencv_highgui", "opencv_videoio", "dlib"])
    env.Append(LINKFLAGS=["-framework", "Accelerate"])  # For LAPACK/BLAS on macOS

elif env["platform"] == "windows":
    env.Append(CPPPATH=["C:/Program Files/opencv/build/include", "C:/Program Files/opencv/build/x64/vc16/lib", "C:/Program Files/opencv/build/opencv2/include", "C:/Users/Pedro/dlib/"])
    env.Append(LIBPATH=["C:/Program Files/opencv/build/x64/vc16/lib"])

    env.Append(LIBS=["opencv_core460",
        "opencv_highgui460",
        "opencv_videoio460", "dlib", "lapack", "blas"])

    env["ENV"]["PATH"] += ";C:/Program Files/opencv/build/x64/vc16/bin"

    env.Append(CCFLAGS=["/EHsc"])  # Enable exception handling on MSVC

env.Append(CCFLAGS=["-fexceptions"] if env["platform"] != "windows" else ["/EHsc"])

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