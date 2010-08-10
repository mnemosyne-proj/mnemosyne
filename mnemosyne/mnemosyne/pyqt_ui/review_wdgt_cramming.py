#
# review_wdgt_cramming.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.review_wdgt import ReviewWdgt
   

class ReviewWdgtCramming(ReviewWdgt):
    
    def __init__(self, component_manager):
        ReviewWdgt.__init__(self, component_manager)
        self.grade_0_button.setText(_("&Wrong"))       
        self.grade_1_button.hide()
        self.line.hide()
        self.grade_2_button.hide()
        self.grade_3_button.hide()
        self.grade_4_button.hide()
        self.grade_5_button.setText(_("&Right"))
        self.grade_5_button.setFocus()
        parent = self.parent()
        self.wrong = QtGui.QLabel("", parent.status_bar)
        self.unseen = QtGui.QLabel("", parent.status_bar)
        self.active = QtGui.QLabel("", parent.status_bar)
        parent.clear_status_bar()
        parent.add_to_status_bar(self.wrong)
        parent.add_to_status_bar(self.unseen)
        parent.add_to_status_bar(self.active)

    def update_status_bar(self, message=None):
        wrong_count, unseen_count, active_count = \
                   self.review_controller().counters()
        self.wrong.setText(_("Wrong: %d ") % wrong_count)
        self.unseen.setText(_("Unseen: %d ") % unseen_count)
        self.active.setText(_("Active: %d ") % active_count)
        if message:
            self.main_widget().status_bar_message(message)