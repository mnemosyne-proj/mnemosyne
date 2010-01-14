#
# utils.py - Peter Bienstman <Peter.Bienstman@UGent.be>

import os
import math


def tar_file_size(basedir, relative_paths):

    """Returns size in bytes of a tar file containing relative paths in a
    given basedir.

    """

    # TODO: estimate only.

    size = 0
    for path in relative_paths:
        raw_size = os.path.getsize(os.path.join(basedir, path))
        # 512 byte header plus file content in blocks of 512 bytes.
        size += 512 + int(math.ceil(raw_size / 512.0)) * 512
    # 2 512 blocks zero to signal end + pad on 10240 byte boundary.
    return int(math.ceil((size + 2*512) / 10240.)) * 10240
    
