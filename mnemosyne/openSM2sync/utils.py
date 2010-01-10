#
# utils.py - Peter Bienstman <Peter.Bienstman@UGent.be>

import os
import math


def tar_file_size(basedir, relative_paths):

    """Returns size in bytes of a tar file containing relative paths in a
    given basedir.

    """

    size = 0
    for path in relative_paths:
        raw_size = os.path.getsize(os.path.join(basedir, path))
        # 512 byte header plus file content in blocks of 512 bytes.
        size += 512 + int(math.ceil(raw_size / 512)) * 512
    return size
    
