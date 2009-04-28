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

from review_wdgt import ReviewWdgt
from mnemosyne.libmnemosyne.main_widget import MainWidget
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import ui_controller_review

class MainFrame(gui.CeFrame, MainWidget):
    
    def __init__(self):
        gui.CeFrame.__init__(self, title=_("Mnemosyne"))
        
        # Total number of cards for statusbar, to be cached.
        self.all_cards = None

        self.review_widget = ReviewWdgt(parent=self)

        self.status_sizer = gui.HBox(spacing=10)
        self.scheduled_label = gui.Label(self)
        self.not_memorised_label = gui.Label(self)
        self.all_label = gui.Label(self)
        self.status_sizer.add(self.scheduled_label)
        self.status_sizer.add(self.not_memorised_label)
        self.status_sizer.add(self.all_label)
        
        sizer = gui.VBox()
        sizer.add(self.review_widget)
        sizer.add(self.status_sizer)
        self.sizer = sizer
   
    def init_review_widget(self):
        ui_controller_review().widget = self.review_widget
        
    def update_status_bar(self):
        db = database()
        self.scheduled_label.text = \
            _("Sch.:") + " " + str(db.scheduled_count())
        self.not_memorised_label.text = \
            _("Not mem.:") + " " + str(db.non_memorised_count())
        if not self.all_cards:
            self.all_cards = db.active_count()
        self.all_label.text = \
            _("All:") + " " + str(self.all_cards)

    def error_box(self, exception):
        if exception.info:
            exception.msg += "\n" + exception.info
        gui.Message.ok(_("Mnemosyne"), exception.msg)
