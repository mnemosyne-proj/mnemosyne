#
# exceptions.py <Peter.Bienstman@UGent.be>
#

import sys
import traceback
import string

from mnemosyne.libmnemosyne.component_manager import component_manager
_ = component_manager.translator


def traceback_string():
    
    """Like traceback.print_exc(), but returns a string."""

    type, value, tb = sys.exc_info()
    body = "\nTraceback (innermost last):\n"
    list = traceback.format_tb(tb, limit=None) + \
           traceback.format_exception_only(type, value)
    body = body + "%-20s %s" % (string.join(list[:-1], ""), list[-1],)
    return body


class MnemosyneError(Exception):

    msg = ""
    
    def __init__(self, stack_trace=False, info=None):
        if stack_trace == True:
            self.info = traceback_string()
        else:
            self.info = info

class ConfigError(MnemosyneError):        
    msg = _("Error in config.py:")

class PluginError(MnemosyneError):
    msg = _("Error when running plugin:")

class LoadError(MnemosyneError):
    msg = _("Unable to load file.")

class LoadErrorCreateTmp(MnemosyneError):
    msg = _("Unable to load database.\nCreating tmp file.")

class MissingPluginError(MnemosyneError):
    msg = _("Missing plugin for card type with id:")

class InvalidFormatError(MnemosyneError):
    msg = _("Invalid file format.")

class SaveError(MnemosyneError):
    msg = _("Unable to save file.")
    
class XMLError(MnemosyneError):
    msg = _("Unable to parse XML:")

class EncodingError(MnemosyneError):
    msg = _("Unrecognised encoding.")

class MissingAnswerError(MnemosyneError):
    msg = _("Missing answer on line:")
