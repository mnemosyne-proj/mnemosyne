#
# main_window.py <Peter.Bienstman@UGent.be>
#

import os

if os.name == "ce":
	import ppygui.api as gui
else:
	import emulator.api as gui

from mnemosyne.libmnemosyne import initialise_user_plugins
from mnemosyne.libmnemosyne.exceptions import MnemosyneError
from mnemosyne.libmnemosyne.component_manager import config, database
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.component_manager import ui_controller_review

from review_wdgt import ReviewWdgt


class MainFrame(gui.CeFrame):
    
    def __init__(self, filename=None):
        gui.CeFrame.__init__(self, title="Mnemosyne")
        self.review_widget = ReviewWdgt(parent=self)
        sizer = gui.VBox()
        sizer.add(self.review_widget)
        self.sizer = sizer

        try:
            initialise_user_plugins()
        except MnemosyneError, e:
            self.error_box(e)
            
        if filename == None:
            filename = config()["path"]
            
        try:
            database().load(filename)
        except MnemosyneError, e:
            self.error_box(e)
            self.error_box(LoadErrorCreateTmp())
            filename = os.path.join(os.path.split(filename)[0], "___TMP___" \
                                    + database().suffix)
            database().new(filename)
            
        ui_controller_main().widget = self
        self.update_review_widget()
        ui_controller_review().new_question()

    def update_review_widget(self):
        ui_controller_review().widget = self.review_widget

    def update_status_bar(self):
        # TODO: move here.
        self.review_widget.update_status_bar()

    def error_box(self, exception):
        if exception.info:
            exception.msg += "\n" + exception.info
        gui.Message.ok("Mnemosyne", exception.msg)
