LOCAL_PATH := $(call my-dir)
CRYSTAX_PATH := C:/crystax-ndk-10.3.2

# Build libpybridge.so

include $(CLEAR_VARS)
LOCAL_MODULE    := pybridge
LOCAL_SRC_FILES := pybridge.c
#LOCAL_CFLAGS += -g
LOCAL_LDLIBS := -llog
LOCAL_SHARED_LIBRARIES := python3.5m
include $(BUILD_SHARED_LIBRARY)

# Include libpython3.5m.so

include $(CLEAR_VARS)
LOCAL_MODULE    := python3.5m
LOCAL_SRC_FILES := $(CRYSTAX_PATH)/sources/python/3.5/libs/$(TARGET_ARCH_ABI)/libpython3.5m.so
LOCAL_EXPORT_CFLAGS := -I $(CRYSTAX_PATH)/sources/python/3.5/include/python/
include $(PREBUILT_SHARED_LIBRARY)

# Python modules dependencies like _sqlite3.so have to be manually copied to
# assets/python, not libs/armeabi-v7a, otherwise Python does not find them.

#include $(CLEAR_VARS)
#LOCAL_MODULE    := _sqlite3
#LOCAL_SRC_FILES := $(CRYSTAX_PATH)/sources/python/3.5/libs/$(TARGET_ARCH_ABI)/modules/_sqlite3.so
#LOCAL_EXPORT_CFLAGS := -I $(CRYSTAX_PATH)/sources/python/3.5/include/python/
#include $(PREBUILT_SHARED_LIBRARY)

