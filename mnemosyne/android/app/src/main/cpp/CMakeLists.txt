cmake_minimum_required(VERSION 3.4.1)

# configure import libs
set(distribution_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../../../dependencies)

# shared lib will also be tucked into APK and sent to target
# refer to app/build.gradle, jniLibs section for that purpose.
# ${ANDROID_ABI} is handy for our purpose here. Probably this ${ANDROID_ABI} is
# the most valuable thing of this sample, the rest are pretty much normal cmake

# add libpython
add_library(lib_python3.7m SHARED IMPORTED)
set_target_properties(lib_python3.7m PROPERTIES IMPORTED_LOCATION
        ${distribution_DIR}/conda-android-python/lib/${ANDROID_ABI}/libpython3.7m.so)

# build pybridge
add_library(pybridge SHARED pybridge.c)
target_include_directories(pybridge PRIVATE ${distribution_DIR}/conda-android-python/include/${ANDROID_ABI})
target_compile_options(pybridge PRIVATE -Wno-unused-value)
target_link_libraries(pybridge
        android
        log
        -lpython3.7m -L${distribution_DIR}/conda-android-python/lib/${ANDROID_ABI}
        )
