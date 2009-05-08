#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4 import QtGui

from ui_review_wdgt import *

from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import component_manager, config
from mnemosyne.libmnemosyne.component_manager import ui_controller_review
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.ui_controllers_review.SM2_controller \
     import SM2Controller

_empty = """
<html><head>
<style type="text/css">
table { height: 100%; }
body  { background-color: white;
        margin: 0;
        padding: 0;
        border: thin solid #8F8F8F; }
</style></head>
<body><table><tr><td></td></tr></table></body></html>
"""

class ReviewWdgt(QtGui.QWidget, Ui_ReviewWdgt, ReviewWidget):

    used_for = SM2Controller
    
    def __init__(self):
        parent = ui_controller_main().widget
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.controller = ui_controller_review()
        self.controller.widget = self
        self.grade_buttons = QtGui.QButtonGroup()
        self.grade_buttons.addButton(self.grade_0_button, 0)
        self.grade_buttons.addButton(self.grade_1_button, 1)
        self.grade_buttons.addButton(self.grade_2_button, 2)
        self.grade_buttons.addButton(self.grade_3_button, 3)
        self.grade_buttons.addButton(self.grade_4_button, 4)
        self.grade_buttons.addButton(self.grade_5_button, 5)
        self.connect(self.grade_buttons, QtCore.SIGNAL("buttonClicked(int)"),\
                     self.grade_answer)
        self.sched = QtGui.QLabel("", self.parent().statusbar)
        self.notmem = QtGui.QLabel("", self.parent().statusbar)
        self.all = QtGui.QLabel("", self.parent().statusbar)
        self.parent().statusbar.addPermanentWidget(self.sched)
        self.parent().statusbar.addPermanentWidget(self.notmem)
        self.parent().statusbar.addPermanentWidget(self.all)
        self.parent().statusbar.setSizeGripEnabled(0)

    def initialise(self):
        self.parent().setCentralWidget(self)

    def finalise(self):
        self.close()

    def show_answer(self):
        self.controller.show_answer()

    def grade_answer(self, grade):
        self.controller.grade_answer(grade)
    
    def enable_edit_current_card(self, enable):
        self.parent().actionEditCurrentCard.setEnabled(enable)

    def enable_delete_current_card(self, enable):      
        self.parent().actionDeleteCurrentFact.setEnabled(enable)

    def enable_edit_deck(self, enable):      
        self.parent().actionEditDeck.setEnabled(enable)

    def question_box_visible(self, visible):
        if visible:
            self.question.show()
            self.question_label.show()
        else:
            self.question.hide()
            self.question_label.hide()

    def answer_box_visible(self, visible):
        if visible:
            self.answer.show()
            self.answer_label.show()
        else:
            self.answer.hide()
            self.question_label.hide()

    def set_question_label(self, text):
        self.question_label.setText(text)

    def set_question(self, text):
        self.question.setHtml(text)

    def set_answer(self, text):
        self.answer.setHtml(text)

    def clear_question(self):
        self.question.setHtml(_empty)
        
    def clear_answer(self):
        self.answer.setHtml(_empty)
        
    def update_show_button(self, text, default, show_enabled):
        self.show_button.setEnabled(show_enabled)
        self.show_button.setText(text)
        self.show_button.setEnabled(show_enabled)
        if default:
            self.show_button.setFocus()

    def enable_grades(self, enabled):
        self.grades.setEnabled(enabled)

    def grade_4_default(self, use_4):
        if use_4:
            self.grade_4_button.setFocus()
        else:
            self.grade_0_button.setFocus()
 
    def set_grades_title(self, text):
        self.grades.setTitle(text)
        
    def set_grade_text(self, grade, text):
        self.grade_buttons.button(grade).setText(text)
        
    def set_grade_tooltip(self, grade, text):
        self.grade_buttons.button(grade).setToolTip(text)

    def update_status_bar(self, message=None):
        db = database()            
        self.sched.setText(_("Scheduled: ") + \
            str(db.scheduled_count()) + " ")
        self.notmem.setText(_("Not memorised: ") + \
            str(db.non_memorised_count()) + " ")
        self.all.setText(_("Active: ") + \
             str(db.active_count()) + " ")
        if message:
            self.parent().statusBar().showMessage(message)
        

# Register widget.

component_manager.register(ReviewWdgt)
