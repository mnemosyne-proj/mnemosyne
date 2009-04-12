#
# utils.py <Peter.Bienstman@UGent.be>
#

import os
import re
import datetime
from mnemosyne.libmnemosyne.component_manager import config

def expand_path(p, prefix=None):

    """Make relative path absolute and normalise slashes."""
    
    # By default, make paths relative to the database location.
    if prefix == None:
        prefix = os.path.dirname(config()["path"])
    # If there was no dirname in the last statement, it was a relative
    # path and we set the prefix to the basedir.
    if prefix == '':
        prefix = config().basedir
    if (    ( (len(p) > 1) and p[0] == "/") \
         or ( (len(p) > 2) and p[1] == ":") ): # Unix or Windows absolute path.
        return os.path.normpath(p)
    else:  
        return os.path.normpath(os.path.join(prefix, p))


def contract_path(p, prefix=None):

    """Make absolute path relative and normalise slashes."""

    # By default, make paths relative to the database location.
    if prefix == None:
        prefix = os.path.dirname(config()["path"])
    # If there was no dirname in the last statement, it was a relative
    # path and we set the prefix to the basedir.
    if prefix == '':
        prefix = config().basedir
    # Normalise paths and convert everything to lowercase on Windows.
    p = os.path.normpath(p)
    prefix = os.path.normpath(prefix)
    if ( (len(p) > 2) and p[1] == ":"):
        p = p.lower()
        prefix = prefix.lower()
    # Do the actual detection.
    if (    ( (len(p) > 1) and p[0] == "/") \
         or ( (len(p) > 2) and p[1] == ":") ): # Unix or Windows absolute path.
        try:
            return p.split(prefix)[1][1:]
        except:
            return p            
    else:
        return p


def numeric_string_cmp(s1, s2):
    
    """Compare two strings using numeric ordering
    
    Compare the two strings s1 and s2 and return an integer according to the 
    outcome. The return value is negative if s1 < s2, zero if s1 == s2 and 
    strictly positive if s1 > s2. Unlike the standard python cmp() function
    numeric_string_cmp() compares strings using a natural numeric ordering,
    so that, e.g., "abc2" < "abc10".

    The strings are first split into tuples consisting of the alphabetic and
    numeric portions of the string. For example, "33_file1.txt" is converted
    to the tuple ('', 33, '_file', 1, '.txt'). The tuples are then compared
    using the standard python cmp().

    """
    
    atoi = lambda s: int(s) if s.isdigit() else s
    scan = lambda s: tuple(atoi(str) for str in re.split('(\d+)', s))
    return cmp(scan(s1), scan(s2))
