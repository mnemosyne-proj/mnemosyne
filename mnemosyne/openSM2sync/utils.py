#
# utils.py - Peter Bienstman <Peter.Bienstman@UGent.be>

import os
import sys
import math
import random
import traceback

class SyncError(Exception):
    pass

def traceback_string():
    
    """Like traceback.print_exc(), but returns a string."""

    type, value, tb = sys.exc_info()
    body = "\nTraceback (innermost last):\n"
    list = traceback.format_tb(tb, limit=None) + \
           traceback.format_exception_only(type, value)
    body = body + "%-20s %s" % ("".join(list[:-1]), list[-1])
    return body

def tar_file_size(basedir, relative_paths):

    """Returns size in bytes of a tar file (PAX format) containing relative
    paths in a given basedir.

    """
    
    if len(relative_paths) == 0:
        return 0
    size = 512 # Global PAX header.
    for path in relative_paths:
        raw_size = os.path.getsize(os.path.join(basedir, path))        
        # PAX: 2 x 512 byte header plus file content in blocks of 512 bytes.
        size += 2*512 + int(math.ceil(raw_size / 512.0)) * 512
    # 2 x 512 blocks zero to signal end + pad on 10240 byte boundary.
    return int(math.ceil((size + 2*512) / 10240.)) * 10240

def rand_uuid():

    """Importing Python's uuid module brings a huge overhead, so we use
    our own variant: a length 22 random string from a 62 letter alphabet,
    which in terms of randomness is about the same as the traditional hex
    string with length 32, but uses less space.

    """
    
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXZY0123456789"
    rand = random.random
    uuid = ""
    for c in range(22):
        uuid += chars[int(rand() * 62.0 - 1)]
    return uuid
