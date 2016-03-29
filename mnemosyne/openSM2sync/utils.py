#
# utils.py - Peter Bienstman <Peter.Bienstman@UGent.be>

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


def file_(filename, mode):
    
    """Wrapped version of file constructor to handle the fact that on
    Android sys.getfilesystemencoding erroneously returns None.
    
    https://code.google.com/p/python-for-android/issues/detail?id=35
    
    """
    
    try:
        return file(filename, mode)
    except (UnicodeEncodeError, UnicodeDecodeError):
        _ENCODING = sys.getfilesystemencoding() or \
            locale.getdefaultlocale()[1] or "utf-8"
        return file(filename.encode(_ENCODING), mode)
    

def path_exists(path):
    
    """Our own version of os.path.exists, to deal with unicode issues
    on Android."""
    
    try:
        return os.path.exists(path)
    except UnicodeEncodeError:
        return os.path.exists(path.encode("utf-8"))
    
    
def path_getsize(path):
    
    """Our own version of os.path.getsize, to deal with unicode issues
    on Android."""
    
    try:
        return os.path.getsize(path)
    except UnicodeEncodeError:
        return os.path.getsize(path.encode("utf-8"))  
  
    
def path_join(path1, path2):
    
    """Our own version of os.path.getsize, to deal with unicode issues
    on Android."""
    
    try:
        return os.path.join(path1, path2)
    except UnicodeDecodeError:
        return os.path.join(path1.decode("utf-8"), path2.decode("utf-8"))      