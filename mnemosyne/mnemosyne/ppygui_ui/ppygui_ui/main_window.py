#
# main_window.py <Peter.Bienstman@UGent.be>
#

import os
if os.name == "ce":
	import ppygui.api as gui
else:
	import emulator.api as gui

from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class MainFrame(gui.CeFrame, MainWidget):
    
    def __init__(self):
        gui.CeFrame.__init__(self, title="Mnemosyne")

    def set_central_widget(self, widget)
        sizer = gui.VBox()
        sizer.add(widget)
        self.sizer = sizer
    
    def information_box(self, message):
        gui.Message.ok("Mnemosyne", message, icon="info")            
        
    def error_box(self, message):
        gui.Message.ok("Mnemosyne", message, icon="error")

    def question_box(self, question, option0, option1, option2):

        """ppygui has no convenience functions for this, so this should be
        created as a custom dialog. However, for just the review client, its
        main use is displaying the dialog that another instance is running,
        so we solve it in a different way.

        """

        raise RuntimeError, question

