#!/usr/bin/env python

#
# Mnemosyne Mobile.py <Peter.Bienstman@UGent.be>
#

import os
if os.name == "ce":
	import ppygui.api as gui
else:
	import emulator.api as gui

# TODO: create mechanism which will make it easier to change the basedir,
# e.g. by a first run wizard, of from an option in the program. Perhaps a
# text file in the location of libmnemosyne?
   basedir = "\SDMMC\.mnemosyne"

# Load the Mnemosyne library (Make sure you haven't imported parts of the
# Mnemosyne library previously, e.g. by importing a GUI class).
from mnemosyne.libmnemosyne import Mnemosyne
Mnemosyne.components = [             
    ("mnemosyne.libmnemosyne.configuration",
     "Configuration"),
    ("mnemosyne.libmnemosyne.databases.SQLite",
     "SQLite"),  
    ("mnemosyne.libmnemosyne.loggers.txt_logger",
     "TxtLogger"),          
    ("mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne",
     "SM2Mnemosyne"),                   
    ("mnemosyne.libmnemosyne.card_types.front_to_back",
     "FrontToBack"),
    ("mnemosyne.libmnemosyne.card_types.both_ways",
     "BothWays"),
    ("mnemosyne.libmnemosyne.card_types.three_sided",
     "ThreeSided"),
    ("mnemosyne.libmnemosyne.renderers.html_css_old",
     "HtmlCssOld"),
    ("mnemosyne.libmnemosyne.filters.escape_to_html",
     "EscapeToHtml"),
    ("mnemosyne.libmnemosyne.filters.expand_paths",
     "ExpandPaths"),
    ("mnemosyne.libmnemosyne.filters.latex",
     "Latex"),
    ("mnemosyne.libmnemosyne.ui_controllers_main.default_main_controller",
     "DefaultMainController"),
    ("mnemosyne.libmnemosyne.ui_controllers_review.SM2_controller",
     "SM2Controller"),
    ("mnemosyne.libmnemosyne.card_types.map",
     "MapPlugin"),
    ("mnemosyne.libmnemosyne.card_types.cloze",
     "ClozePlugin"),
    ("mnemosyne.libmnemosyne.schedulers.cramming",
     "CrammingPlugin") ]
mnemosyne = Mnemosyne(resource_limited=True)

# Start Mnemosyne.
app = gui.Application()
from mnemosyne.ppygui_ui.main_window import MainFrame
app.mainframe = MainFrame()
mnemosyne.initialise(basedir=basedir, main_widget=app.mainframe)
app.run()
mnemosyne.finalise()
