#!/usr/bin/env python

#
# Mnemosyne Mobile.py <Peter.Bienstman@UGent.be>
#

import os
if os.name == "ce":
	import ppygui.api as gui
else:
	import emulator.api as gui

from main_window import MainFrame

from mnemosyne.libmnemosyne import Mnemosyne

# TODO: create mechanism which will make it easier to change the basedir,
# e.g. by a first run wizard, of from an option in the program. Perhaps a
# text file in the location of libmnemosyne?
   
basedir = "\\SDMMC"

app = gui.Application()
app.mainframe = MainFrame()
mnemosyne = Mnemosyne(resource_limited=True)
mnemosyne.initialise(basedir=basedir, main_widget=app.mainframe)
app.run()
mnemosyne.finalise()
