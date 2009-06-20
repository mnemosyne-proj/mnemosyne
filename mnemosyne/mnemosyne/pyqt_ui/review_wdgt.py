#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from ui_review_wdgt import *
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class ReviewWdgt(QtGui.QWidget, Ui_ReviewWdgt, ReviewWidget):

    _empty = """
        <html><head>
        <style type="text/css">
        table { height: 100%; }
        body  { background-color: white;
                margin: 0;
                padding: 0;
                border: thin solid #8F8F8F; }
        </style></head>
        <body><table><tr><td></td></tr></table></body></html>"""

    auto_focus_grades = True
    
    def __init__(self, component_manager):
        ReviewWidget.__init__(self, component_manager)
        parent = self.main_widget()
        QtGui.QWidget.__init__(self, parent)
        parent.setCentralWidget(self)
        self.setupUi(self)
        self.grade_buttons = QtGui.QButtonGroup()
        self.grade_buttons.addButton(self.grade_0_button, 0)
        self.grade_buttons.addButton(self.grade_1_button, 1)
        self.grade_buttons.addButton(self.grade_2_button, 2)
        self.grade_buttons.addButton(self.grade_3_button, 3)
        self.grade_buttons.addButton(self.grade_4_button, 4)
        self.grade_buttons.addButton(self.grade_5_button, 5)
        self.connect(self.grade_buttons, QtCore.SIGNAL("buttonClicked(int)"),\
                     self.grade_answer)
        self.sched = QtGui.QLabel("", parent.statusbar)
        self.notmem = QtGui.QLabel("", parent.statusbar)
        self.act = QtGui.QLabel("", parent.statusbar)
        parent.clear_statusbar()
        parent.add_to_statusbar(self.notmem)
        parent.add_to_statusbar(self.sched)
        parent.add_to_statusbar(self.act)
        parent.statusbar.setSizeGripEnabled(0)

    def show_answer(self):
        self.ui_controller_review().show_answer()

    def grade_answer(self, grade):
        self.ui_controller_review().grade_answer(grade)

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
        self.question.setHtml(self._empty)
        
    def clear_answer(self):
        self.answer.setHtml(self._empty)
        
    def update_show_button(self, text, default, show_enabled):
        self.show_button.setEnabled(show_enabled)
        self.show_button.setText(text)
        self.show_button.setEnabled(show_enabled)
        if default:
            self.show_button.setDefault(True)
            self.show_button.setFocus()

    def enable_grades(self, enabled):
        self.grades.setEnabled(enabled)

    def set_default_grade(self, grade):
        if self.auto_focus_grades:
            self.grade_buttons.button(grade).setFocus()
 
    def set_grades_title(self, text):
        self.grades.setTitle(text)
        
    def set_grade_text(self, grade, text):
        self.grade_buttons.button(grade).setText(text)
        
    def set_grade_tooltip(self, grade, text):
        self.grade_buttons.button(grade).setToolTip(text)

    def update_status_bar(self, message=None):
        non_memorised_count, scheduled_count, active_count = \
                   self.ui_controller_review().get_counters()
        self.notmem.setText(_("Not memorised: %d ") % non_memorised_count)
        self.sched.setText(_("Scheduled: %d ") % scheduled_count)
        self.act.setText(_("Active: %d ") % active_count)
        if message:
            self.parent().statusBar().showMessage(message)
