##############################################################################
#
# utils.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import os
from mnemosyne.libmnemosyne.config import config



##############################################################################
#
# expand_path
#
#   Make relative path absolute and normalise slashes.
#
##############################################################################

def expand_path(p, prefix=None):
    
    # By default, make paths relative to the database location.

    if prefix == None:
        prefix = os.path.dirname(config["path"])

    # If there was no dirname in the last statement, it was a relative
    # path and we set the prefix to the basedir.
    
    if prefix == '':
        prefix = config.basedir

    if (    ( (len(p) > 1) and p[0] == "/") \
         or ( (len(p) > 2) and p[1] == ":") ): # Unix or Windows absolute path.
        return os.path.normpath(p)
    else:  
        return os.path.normpath(os.path.join(prefix, p))



##############################################################################
#
# contract_path
#
#   Make absolute path relative and normalise slashes.
#
##############################################################################

def contract_path(p, prefix=None):

    # By default, make paths relative to the database location.

    if prefix == None:
        prefix = os.path.dirname(get_config("path"))

    # If there was no dirname in the last statement, it was a relative
    # path and we set the prefix to the basedir.
    
    if prefix == '':
        prefix = config.basedir

    if (    ( (len(p) > 1) and p[0] == "/") \
         or ( (len(p) > 2) and p[1] == ":") ): # Unix or Windows absolute path.
        try:
            return p.split(prefix)[1][1:]
        except:
            return p            
    else:
        return p
