LOCAL_PATH := $(call my-dir)

# Build libpybridge.so

include $(CLEAR_VARS)
LOCAL_MODULE    := pybridge
LOCAL_SRC_FILES := pybridge.c
#LOCAL_CFLAGS += -g
#LOCAL_LDLIBS := -llog
LOCAL_SHARED_LIBRARIES := python3.7m
include $(BUILD_SHARED_LIBRARY)

