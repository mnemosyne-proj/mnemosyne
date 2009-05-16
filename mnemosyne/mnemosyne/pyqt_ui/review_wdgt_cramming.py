#
# review_wdgt_cramming.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4 import QtGui

from review_wdgt import ReviewWdgt

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.schedulers.cramming import Cramming
   

class ReviewWdgtCramming(ReviewWdgt):

    instantiate = Component.WHEN_PLUGIN_ACTIVE
    
    def __init__(self):
        ReviewWdgt.__init__(self)
        self.grade_0_button.setText(_("&Wrong"))       
        self.grade_1_button.hide()
        self.line.hide()
        self.grade_2_button.hide()
        self.grade_3_button.hide()
        self.grade_4_button.hide()
        self.grade_5_button.setText(_("&Right"))
        self.grade_5_button.setFocus()
        parent = self.parent()
        self.wrong = QtGui.QLabel("", parent.statusbar)
        self.unseen = QtGui.QLabel("", parent.statusbar)
        self.active = QtGui.QLabel("", parent.statusbar)
        parent.clear_statusbar()
        parent.add_to_statusbar(self.wrong)
        parent.add_to_statusbar(self.unseen)
        parent.add_to_statusbar(self.active)

    def update_status_bar(self, message=None):
        db = database()            
        self.wrong.setText(_("Wrong: ") + \
            str(db.scheduler_data_count(Cramming.WRONG)) + " ")
        self.unseen.setText(_("Unseen: ") + \
            str(db.scheduler_data_count(Cramming.UNSEEN)) + " ")
        self.active.setText(_("Active: ") + \
            str(db.active_count()) + " ")
        if message:
            self.parent().statusBar().showMessage(message)
