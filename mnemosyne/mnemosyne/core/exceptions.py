##############################################################################
#
# Mnemosyne exceptions <Peter.Bienstman@UGent.be>
#
##############################################################################

import sys, traceback, string



##############################################################################
#
# Like traceback.print_exc(), but returns a string
#
##############################################################################

def traceback_string():

    type, value, tb = sys.exc_info()
    
    body = "\nTraceback (innermost last):\n"
    list = traceback.format_tb(tb, limit=None) + \
           traceback.format_exception_only(type, value)
    body = body + "%-20s %s" % (string.join(list[:-1], ""), list[-1],)
    
    return body



##############################################################################
#
# MnemosyneError
#
##############################################################################

class MnemosyneError(Exception):

    msg = '' # Will be filled in by the UI, to allow translation.
    
    def __init__(self, stack_trace=False, info=None):
        if stack_trace == True:
            self.info = traceback_string()
        else:
            self.info = info



##############################################################################
#
# Derived errors
#
##############################################################################

class ConfigError(MnemosyneError):
    pass

class PluginError(MnemosyneError):
    pass

class LoadError(MnemosyneError):
    pass

class LoadErrorCreateTmp(MnemosyneError):
    pass

class InvalidFormatError(MnemosyneError):
    pass

class SaveError(MnemosyneError):
    pass

class XMLError(MnemosyneError):
    pass

class EncodingError(MnemosyneError):
    pass

class MissingAnswerError(MnemosyneError):
    pass
