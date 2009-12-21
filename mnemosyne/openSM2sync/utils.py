#
# utils.py - Peter Bienstman <Peter.Bienstman@UGent.be>
#

import os


def create_subdirs(prefix, filename):

    """'filename' is a path considered relative to the 'prefix' directory.
    If 'filename' contains directories which don't exist yet, create
    them inside the 'prefix' directory.

    """

    # Convert Windows separators to Unix separators.
    filename = filename.replace("\\", "/")
    # Create subdirs
    parent_dir = prefix
    while "/" in filename:
        head, tail = filename.split("/", 1)
        parent_dir = os.path.join(parent_dir, head)
        if not os.path.exists(parent_dir):
            os.mkdir(parent_dir)
        filename = tail
            
