#!/usr/bin/env python

#
# Mnemosyne Mobile.py <Peter.Bienstman@UGent.be>
#

import os
if os.name == "ce":
	import ppygui.api as gui
else:
	import mnemosyne.ppygui_ui.emulator.api as gui

from mnemosyne.libmnemosyne import Mnemosyne

# TODO: create mechanism which will make it easier to change the data_dir,
# e.g. by a first run wizard, of from an option in the program. Perhaps a
# text file in the location of libmnemosyne?
data_dir = "\SDMMC\mnemosyne2"

# Load the Mnemosyne library.
mnemosyne = Mnemosyne(upload_science_logs=False)

# Initialise GUI toolkit.
app = gui.Application()

# List the components we use. The translator should obviously come first, and
# the UI components should come in the order they should be instantiated, but
# apart from that, the order does not matter.
mnemosyne.components = [
    ("mnemosyne.libmnemosyne.translator",
     "NoTranslation"),
    ("mnemosyne.ppygui_ui.main_wdgt",
     "MainWdgt"),
    ("mnemosyne.ppygui_ui.review_wdgt",
     "ReviewWdgt"),
    ("mnemosyne.ppygui_ui.render_chain_WM",
     "RenderChain_WM"),
    ("mnemosyne.libmnemosyne.databases.SQLite_no_pregenerated_data",
     "SQLite_NoPregeneratedData"),
    ("mnemosyne.libmnemosyne.configuration",
     "Configuration"),
    ("mnemosyne.libmnemosyne.loggers.database_logger",
     "DatabaseLogger"),
    ("mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne",
     "SM2Mnemosyne"),
    ("mnemosyne.libmnemosyne.stopwatch",
     "Stopwatch"),
    ("mnemosyne.libmnemosyne.card_types.front_to_back",
     "FrontToBack"),
    ("mnemosyne.libmnemosyne.card_types.both_ways",
     "BothWays"),
    ("mnemosyne.libmnemosyne.card_types.three_sided",
     "ThreeSided"),
    ("mnemosyne.libmnemosyne.controllers.default_controller",
     "DefaultController"),
    ("mnemosyne.libmnemosyne.review_controllers.SM2_controller",
     "SM2Controller"),
    ("mnemosyne.libmnemosyne.card_types.map",
     "MapPlugin"),
    ("mnemosyne.libmnemosyne.card_types.cloze",
     "ClozePlugin"),
    ("mnemosyne.libmnemosyne.criteria.default_criterion",
     "DefaultCriterion"),
    ("mnemosyne.libmnemosyne.databases.SQLite_criterion_applier",
     "DefaultCriterionApplier") ]

# Run Mnemosyne.
mnemosyne.initialise(data_dir=data_dir)
mnemosyne.start_review()
app.mainframe = mnemosyne.main_widget()
app.run()
mnemosyne.finalise()