# Migrate to: https://github.com/android/ndk-samples/tree/master/hello-libs

# https://stackoverflow.com/questions/9870435/how-to-link-a-prebuilt-shared-library-to-an-android-ndk-project

LOCAL_PATH := $(call my-dir)

# libpython3.7m
include $(CLEAR_VARS)
LOCAL_MODULE := python3.7m
LOCAL_SRC_FILES := $(LOCAL_PATH)/../conda-android-python/$(TARGET_ARCH_ABI)/lib/libpython3.7m.so
LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/../conda-android-python/$(TARGET_ARCH_ABI)/include/python3.7m
include $(PREBUILT_SHARED_LIBRARY)

# libpybridge.so
include $(CLEAR_VARS)
LOCAL_MODULE := pybridge
LOCAL_SRC_FILES := pybridge.c
LOCAL_LDLIBS := -llog
# Unsuccessful workaround: https://github.com/android/ndk-samples/issues/364
LOCAL_CFLAGS += -L$(LOCAL_PATH)/../conda-android-python/$(TARGET_ARCH_ABI)/lib
LOCAL_SHARED_LIBRARIES := python3.7m
include $(BUILD_SHARED_LIBRARY)