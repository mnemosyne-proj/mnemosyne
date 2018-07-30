#
# utf8_filenames.py <Peter.Bienstman@UGent.be>
#

# In some cases, Python 3.5 in Crystax seems to set sys.setdefaultencoding() to
# "ascii", although the Android filesystem supports UTF-8. Therefore, we wrap
# all builtin functions to encode the filenames.

import os
import builtins

def open(filename, *a, **kw):
    try:
        return builtins.open(filename, *a, **kw)
    except:
        filename = filename.encode("utf-8") if type(filename) == str else filename
        return builtins.open(filename, *a, **kw)

_os_path_exists_orig = os.path.exists
def os_path_exists_utf8(filename, *a, **kw):
    try:
        return _os_path_exists_orig(filename, *a, **kw)
    except:
        filename = filename.encode("utf-8") if type(filename) == str else filename
        return _os_path_exists_orig(filename, *a, **kw)
os.path.exists = os_path_exists_utf8

_os_path_getsize_orig = os.path.getsize
def os_path_getsize_utf8(filename, *a, **kw):
    try:
        return _os_path_getsize_orig(filename, *a, **kw)
    except:
        filename = filename.encode("utf-8") if type(filename) == str else filename
        return _os_path_getsize_orig(filename, *a, **kw)
os.path.getsize = os_path_getsize_utf8

