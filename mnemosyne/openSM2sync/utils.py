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

    """Returns size in bytes of a tar file containing relative paths in a
    given basedir.

    """

    # TODO: estimate only.

    size = 0
    if len(relative_paths) == 0:
        return 0
    for path in relative_paths:
        raw_size = os.path.getsize(os.path.join(basedir, path))
        # 512 byte header plus file content in blocks of 512 bytes.
        size += 512 + int(math.ceil(raw_size / 512.0)) * 512
    # 2 512 blocks zero to signal end + pad on 10240 byte boundary.
    return int(math.ceil((size + 2*512) / 10240.)) * 10240

def rand_uuid():

    """Importing Python's uuid module brings a huge overhead, so we use
    this stand-alone version from 
    http://www.python-forum.org/pythonforum/viewtopic.php?f=14&t=6269

    """

    uuid = [0,0,0,0,0]
    chars = "abcdef0123456789"
    rand = random.random
    for g,length in enumerate([8, 4, 4, 4, 12]):
        seg = ""
        for i in range(length):
            seg += chars[int(rand() * 16.0 - 1)]
        uuid[g] = seg
    return "-".join(uuid)
