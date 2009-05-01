#
# review_wdgt_cramming.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from review_wdgt import ReviewWdgt

from mnemosyne.libmnemosyne.schedulers.cramming import Cramming
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import component_manager


class ReviewWdgtCramming(ReviewWdgt):
    
    def __init__(self, parent=None):
        ReviewWdgt.__init__(self.parent)
        self.grade_0_button.setText(_("Right"))       
        self.grade_1_button.hide()
        self.grade_2_button.hide()
        self.grade_3_button.hide()
        self.grade_4_button.hide()
        self.grade_5_button.setText(_("Wrong"))

    def grade_4_default(self, use_4):
        # Rather than writing a new controller, we just hijack this function
        # to set grade 5 always as the default.
        self.grade_5_button.setFocus()
  
    def set_grade_tooltip(self, grade, text):
        self.grade_buttons.button(grade).setToolTip("")

    def update_status_bar(self, message=None):
        db = database()            
        self.sched.setText(_("Wrong: ") + \
            str(db.scheduler_data_count(Cramming.WRONG)) + " ")
        self.notmem.setText(_("Unseen: ") + \
            str(db.scheduler_data_count(Cramming.UNSEEN)) + " ")
        self.all.setText(_("Active: ") + \
            str(db.active_count()) + " ")
        if message:
            self.parent().statusBar().showMessage(message)
        

# Register widget.

component_manager.register("review_widget", ReviewWdgtCramming,
                           used_for=Cramming)
