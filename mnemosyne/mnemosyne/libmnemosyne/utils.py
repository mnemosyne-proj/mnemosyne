#
# utils.py <Peter.Bienstman@UGent.be>
#

import os
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
        prefix = os.path.dirname(config()("path"))
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
