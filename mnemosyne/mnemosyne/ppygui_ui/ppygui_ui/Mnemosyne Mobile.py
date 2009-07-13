#!/usr/bin/env python

#
# Mnemosyne Mobile.py <Peter.Bienstman@UGent.be>
#

import os
if os.name == "ce":
	import ppygui.api as gui
else:
	import emulator.api as gui

from mnemosyne.libmnemosyne import Mnemosyne

# TODO: create mechanism which will make it easier to change the basedir,
# e.g. by a first run wizard, of from an option in the program. Perhaps a
# text file in the location of libmnemosyne?
basedir = "\SDMMC\.mnemosyne"

# Load the Mnemosyne library.
mnemosyne = Mnemosyne(resource_limited=True)

# Initialise GUI toolkit.
app = gui.Application()

# List the components we use. The translator should obviously come first, and
# the UI components should come in the order they should be instantiated, but
# apart from that, the order does not matter.
mnemosyne.components = [
    ("mnemosyne.libmnemosyne.translator",
     "NoTranslation"),    
    ("mnemosyne.ppygui_ui.main_window",
     "MainFrame"),
    ("mnemosyne.ppygui_ui.review_wdgt",
     "ReviewWdgt"),
    ("mnemosyne.libmnemosyne.databases.SQLite",
     "SQLite"), 
    ("mnemosyne.libmnemosyne.configuration",
     "Configuration"), 
    ("mnemosyne.libmnemosyne.loggers.sql_logger",
     "SqlLogger"),          
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
    ("mnemosyne.libmnemosyne.controllers.default_controller",
     "DefaultController"),
    ("mnemosyne.libmnemosyne.review_controllers.SM2_controller",
     "SM2Controller"),
    ("mnemosyne.libmnemosyne.card_types.map",
     "MapPlugin"),
    ("mnemosyne.libmnemosyne.card_types.cloze",
     "ClozePlugin"),
    ("mnemosyne.libmnemosyne.plugins.cramming_plugin",
     "CrammingPlugin") ]

# Run Mnemosyne.
mnemosyne.initialise(basedir=basedir)
app.mainframe = mnemosyne.main_widget()
app.run()
mnemosyne.finalise()
