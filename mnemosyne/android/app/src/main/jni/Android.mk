# https://stackoverflow.com/questions/9870435/how-to-link-a-prebuilt-shared-library-to-an-android-ndk-project

LOCAL_PATH := $(call my-dir)

# libpython3.7m
include $(CLEAR_VARS)
LOCAL_MODULE := python3.7m
LOCAL_SRC_FILES := ../jniLibs/$(TARGET_ARCH_ABI)/libpython3.7m.so
# TODO: better dir
LOCAL_EXPORT_C_INCLUDES := C:/Users/peter/.conda/envs/testapp/android/$(TARGET_ARCH_ABI)/include/python3.7m
include $(PREBUILT_SHARED_LIBRARY)

# libpybridge.so
include $(CLEAR_VARS)
LOCAL_MODULE    := pybridge
LOCAL_SRC_FILES := pybridge.c
LOCAL_LDLIBS :=  -llog
LOCAL_SHARED_LIBRARIES := python3.7m
include $(BUILD_SHARED_LIBRARY)