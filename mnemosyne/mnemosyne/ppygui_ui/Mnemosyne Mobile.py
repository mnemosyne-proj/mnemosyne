#!/usr/bin/env python

#
# Mnemosyne Mobile.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

import sys
import os
import locale
from optparse import OptionParser

from mnemosyne.libmnemosyne import initialise, finalise
from mnemosyne.libmnemosyne.component_manager import config
from mnemosyne.libmnemosyne.exceptions import MnemosyneError

if os.name == "ce":
	import ppygui.api as gui
else:
	import emulator.api as gui
    
from main_window import MainFrame

# Parse options.

parser = OptionParser()
parser.usage = "%prog [<database.mem>]"
parser.add_option("-d", "--datadir", dest="datadir",
                  help="data directory", default=None)
(options, args) = parser.parse_args()

# Check if we have to override the basedir determined in mnemosyne.core,
# either because we explicitly specified a datadir on the command line,
# or because there is a .mnemosyne directory present in the current directory.
# The latter is handy when Mnemosyne is run from a USB key, so that there
# is no need to refer to a drive letter which can change from computer to
# computer.
   
basedir = ""
if options.datadir != None:
    basedir = os.path.abspath(options.datadir)
elif os.path.exists(os.path.join(os.getcwdu(), ".mnemosyne")):
    basedir = os.path.abspath(os.path.join(os.getcwdu(), ".mnemosyne"))
elif os.path.exists(os.path.join(os.getcwdu(), "_mnemosyne")):
    basedir = os.path.abspath(os.path.join(os.getcwdu(), "_mnemosyne"))


# Filename argument.
if len(args) > 0:
    filename = os.path.abspath(args[0])
else:
    filename = None

sys.path.insert(0, basedir)

config_file_c = os.path.join(basedir, "config.pyc")
if os.path.exists(config_file_c):
    os.remove(config_file_c)

try:
    import config as _config
    if _config.locale != None:
        loc = _config.locale      
except:
    pass

# TODO: Install translator.

# TODO: Check if there is another instance of Mnemosyne running.

# Start program.

initialise(basedir)

app = gui.Application()
app.mainframe = MainFrame()
app.run()

finalise()
