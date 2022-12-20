#
# utils.py <Peter.Bienstman@gmail.com>
#          <Johannes.Baiter@gmail.com>
#

import os
import re
import sys
import stat
import html
import random
import traceback

# The following functions are modified from shutil:
#
# - buffer is much larger than the default 16kB in order to improve
#   performance.
# - mode bits are not copied since python on Android does not like this

def copyfileobj(fsrc, fdst, length=8*1024*1024):
    """copy data from file-like object fsrc to file-like object fdst"""
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)

def _samefile(src, dst):
    # Macintosh, Unix.
    if hasattr(os.path, 'samefile'):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    # All other platforms: check for same pathname.
    return (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))

def copyfile(src, dst):
    """Copy data from src to dst"""
    if _samefile(src, dst):
        raise Error("`%s` and `%s` are the same file" % (src, dst))

    for fn in [src, dst]:
        try:
            st = os.stat(fn)
        except OSError:
            # File most likely does not exist
            pass
        else:
            # XXX What about other special files? (sockets, devices...)
            if stat.S_ISFIFO(st.st_mode):
                raise SpecialFileError("`%s` is a named pipe" % fn)

    fsrc = None
    fdst = None
    try:
        fsrc = open(src, 'rb')
        fdst = open(dst, 'wb')
        copyfileobj(fsrc, fdst)
    finally:
        if fdst:
            fdst.close()
        if fsrc:
            fsrc.close()

def copymode(src, dst):
    """Copy mode bits from src to dst"""
    if hasattr(os, 'chmod'):
        st = os.stat(src)
        mode = stat.S_IMODE(st.st_mode)
        os.chmod(dst, mode)

def copy(src, dst):
    """Copy data and mode bits ("cp src dst").

    The destination may be a directory.

    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst)
    #copymode(src, dst)

#
# Memosyne-specific functions.
#

class MnemosyneError(Exception):
    pass


def _abs_path(path):

    """Our own version of os.path.abspath, which does not check for platform.
    In this way, we can test Windows paths even when running the testsuite
    under Linux.

    """

    return    ((len(path) > 1) and path[0] == "/") \
           or ((len(path) > 2) and path[1] == ":")


def contract_path(path, start):

    """Return relative path to 'path' from the directory 'start'.

    All paths in Mnemosyne are internally stored with Unix separators /.

    """

    # Normalise paths.
    path = os.path.normpath(path)
    start = os.path.normpath(start)
    # Do the actual detection.
    if _abs_path(path):
        try:
            rel_path = path.split(start)[1][1:]
        except:
            rel_path = path
    else:
        rel_path = path
    return rel_path.replace("\\", "/")


def expand_path(path, start):

    """Make 'path' absolute starting from 'start'.

    Also convert Unix separators to Windows separators on that platform.

    """

    if _abs_path(path):
        return os.path.normpath(path)
    else:
        return os.path.normpath(os.path.join(start, path))


def normalise_path(path):

    """Make sure the correct types of slashes are used.
    'pathlib' itself turns out to be not sufficient for that.

    """

    if os.name == "posix":
        return path.replace("\\", "/")
    else:
        return path.replace("/", "\\")


def make_filename_unique(filename):
    if os.path.exists(filename):
        prefix, suffix = filename.rsplit(".", 1)
        count = 0
        while True:
            count += 1
            filename = "%s_%d.%s" % (prefix, count, suffix)
            if not os.path.exists(filename):
                break
    return filename


def copy_file_to_dir(filename, dirname):

    """If the file is not in the directory, copy it there. Return the relative
    path to that file inside the directory.

    """

    filename = os.path.abspath(filename)
    dirname = os.path.abspath(dirname)
    if filename.startswith(dirname):
        return contract_path(filename, dirname)
    dest_path = os.path.join(dirname, os.path.basename(\
        filename.replace(':', '-')))
    dest_path = make_filename_unique(dest_path)
    copy(filename, dest_path)
    return contract_path(dest_path, dirname)

def remove_empty_dirs_in(path, level=0):
    # Remove empty subfolders.
    for f in os.listdir(path):
        fullpath = os.path.join(path, f)
        if os.path.isdir(fullpath):
            remove_empty_dirs_in(fullpath, level+1)
    # If the directory is empty, delete it.
    if level !=  0 and len(os.listdir(path)) == 0:
        os.rmdir(path)


def is_filesystem_case_insensitive():
    # We don't import tempfile at module level, since it can crash some
    # Android versions. (This function is not needed on Android devices
    # anyhow.)
    import tempfile
    # By default mkstemp() creates a file with a name that begins with
    # 'tmp' (lowercase)
    tmp_handle, tmp_path = tempfile.mkstemp()
    tmp_file = os.fdopen(tmp_handle, "w")
    result = os.path.exists(tmp_path.upper())
    tmp_file.close()
    os.remove(tmp_path)
    return result


def numeric_string_cmp_key(s):

    """Key for comparing two strings using numeric ordering. so that, e.g.,
    "abc2" < "abc10".

    The strings are first split into tuples consisting of the alphabetic and
    numeric portions of the string. For example, "33_file1.txt" is converted
    to the tuple ('', 33, '_file', 1, '.txt'). The tuples are then compared
    using the standard python cmp().

    """

    atoi = lambda s: int(s) if s.isdigit() else s.lower()
    return tuple(atoi(str) for str in re.split('(\d+)', s))


def traceback_string():

    """Like traceback.print_exc(), but returns a string."""

    type, value, tb = sys.exc_info()
    body = "\nTraceback (innermost last):\n"
    list = traceback.format_tb(tb, limit=None) + \
           traceback.format_exception_only(type, value)
    body = body + "%-20s %s" % ("".join(list[:-1]), list[-1])
    del tb  # Prevent circular references.
    return body


re1 = re.compile(r"<[^>]*?>", re.DOTALL | re.IGNORECASE)
def strip_tags(string):
    return re1.sub("", string)


def mangle(string):

    """Massage string such that it can be used as an identifier."""

    string = html.escape(string)
    if string[0].isdigit():
        string = "_" + string
    new_string = ""
    for char in string:
        if char.isalnum() or char == "_":
            new_string += char
    return new_string


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



class CompareOnId(object):

    """When pulling the same object twice from an SQL database, the resulting
    Python objects will be separate entities. That's why we need to compare
    them on id.

    """

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, CompareOnId):
            return self.id == other.id
        return NotImplemented  # So Python can try other.__eq__(self)

    def __ne__(self, other):

        """Not automatically overridden by overriding __eq__!"""

        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result



# Hack to determine local IP.

def localhost_IP():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("google.com", 8000))
        return s.getsockname()[0]
    except Exception as e:
        return socket.gethostbyname(socket.getfqdn())
