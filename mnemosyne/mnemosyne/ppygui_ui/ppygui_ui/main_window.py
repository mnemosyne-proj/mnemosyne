#
# main_window.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

import os
if os.name == "ce":
	import ppygui.api as gui
else:
	import emulator.api as gui

from mnemosyne.ppygui_ui.review_wdgt import ReviewWdgt
from mnemosyne.libmnemosyne.main_widget import MainWidget
from mnemosyne.libmnemosyne.component_manager import ui_controller_review

class MainFrame(gui.CeFrame, MainWidget):
    
    def __init__(self):
        gui.CeFrame.__init__(self, title=_("Mnemosyne"))
        self.review_widget = ReviewWdgt(parent=self)
        sizer = gui.VBox()
        sizer.add(self.review_widget)
        self.sizer = sizer
   
    def init_review_widget(self):
        ui_controller_review().widget = self.review_widget
        
    def update_status_bar(self):
        self.review_widget.update_status_bar()
    
    def information_box(self, message):
        gui.Message.ok(_("Mnemosyne"), message, icon="info")            
        
    def error_box(self, message):
        gui.Message.ok(_("Mnemosyne"), message, icon="error")

    def question_box(self, question, option0, option1, option2):

        """ppygui has no convenience functions for this, so this should be
        created as a custom dialog. However, for just the review client, its
        main use is displaying the dialog that another instance is running,
        so we solve it in a different way.

        """

        raise Exception(question)
    
