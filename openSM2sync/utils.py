#
# utils.py - Peter Bienstman <Peter.Bienstman@gmail.com>

import os
import sys
import math
import random
import locale
import traceback

class SyncError(Exception):
    pass


class SeriousSyncError(Exception):

    """Requires backup from database afterwards."""
    pass


def traceback_string():

    """Like traceback.print_exc(), but returns a string."""

    type, value, tb = sys.exc_info()
    body = "\nTraceback (innermost last):\n"
    list = traceback.format_tb(tb, limit=None) + \
           traceback.format_exception_only(type, value)
    body = body + "%-20s %s" % ("".join(list[:-1]), list[-1])
    del tb  # Prevent circular references.
    return body


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


def normalise_path(path):

    """Make sure the correct types of slashes are used.
    'pathlib' itself turns out to be not sufficient for that.

    """

    if os.name == "posix":
        return path.replace("\\", "/")
    else:
        return path.replace("/", "\\")

def join_path(base_dir: str, filename: str) -> str:

    """Joins base_dir with filename, raises an execption in case of
    directory traversal (i.e. when the joined path is outside base_dir)."""

    # Make sure that base_dir ends with a /, see
    # https://stackoverflow.com/q/2736144
    base_dir_trail = os.path.join(base_dir, "")
    path = os.path.join(base_dir, filename)
    absolute_path = os.path.realpath(path)

    if os.path.commonprefix((base_dir, absolute_path)) == base_dir:
        return absolute_path
    else:
        raise ValueError("Path outside base directory: " + absolute_path)
