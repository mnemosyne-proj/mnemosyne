#!/usr/bin/env python

##############################################################################
#
# Mnemosyne <Peter.Bienstman@UGent.be>
#
##############################################################################

import sys, os, locale
import mnemosyne.ppygui_ui.simulator.api as gui

#from mnemosyne.core import basedir, get_config, set_config, \
#                           initialise, finalise
#from mnemosyne.core import *
from mnemosyne.ppygui_ui.main_dlg import *
from optparse import OptionParser

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
   
basedir = '' 
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

# Create main widget.
#a = QApplication(sys.argv)

# Under Windows, move out of library.zip to get the true prefix.

if sys.platform == "win32":
    prefix = os.path.split(prefix)[0]
    prefix = os.path.split(prefix)[0]
    prefix = os.path.split(prefix)[0]
    print ("prefix: " + prefix)


# Get the locale from the user's config.py, to install the translator as
# soon as possible.

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

# Install translator.

# Check if there is another instance of Mnemosyne running.



#        sys.exit()
#initialise(basedir)

# Start program.

#w = MainDlg(filename)

#if get_config("first_run") == True:
#    set_config("first_run", False)
#
#if filename == None:
#    filename = get_config("path")
#
#load_database(filename)

app = gui.Application()
app.mainframe = MainFrame()
app.run()

# Execute loop here

finalise()
