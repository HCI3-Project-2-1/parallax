#!/usr/bin/env python
import os
import sys

env = SConscript("include/godot-cpp/SConstruct")

# For reference:
# - CCFLAGS are compilation flags shared between C and C++
# - CFLAGS are for C-specific compilation flags
# - CXXFLAGS are for C++-specific compilation flags
# - CPPFLAGS are for pre-processor flags
# - CPPDEFINES are for pre-processor defines
# - LINKFLAGS are for linking flags

# tweak this if you want to use different folders, or more folders, to store your source code in.
env.Append(CPPPATH=["src/"])
godot_project_bin = "godot_project/bin"
library_name = "libopencv"
sources = Glob("src/engine/*.cpp")

if env["platform"] == "macos":
    library = env.SharedLibrary(
        "{}/{}.{}.{}.framework/{}.{}.{}".format(
            godot_project_bin, library_name, env["platform"], env["target"], env["platform"], env["target"]
        ),
        source=sources,
    )
else:
    library = env.SharedLibrary(
        "{}/{}{}{}".format(godot_project_bin, library_name, env["suffix"], env["SHLIBSUFFIX"]),
        source=sources,
    )

Default(library)
