#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_review_wdgt import Ui_ReviewWdgt
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
        # TODO: move this to designer with update of PyQt.
        self.grade_buttons = QtGui.QButtonGroup()
        self.grade_buttons.addButton(self.grade_0_button, 0)
        self.grade_buttons.addButton(self.grade_1_button, 1)
        self.grade_buttons.addButton(self.grade_2_button, 2)
        self.grade_buttons.addButton(self.grade_3_button, 3)
        self.grade_buttons.addButton(self.grade_4_button, 4)
        self.grade_buttons.addButton(self.grade_5_button, 5)
        self.grade_buttons.buttonClicked[int].connect(self.grade_answer)
        self.focus_widget = None
        self.sched = QtGui.QLabel("", parent.status_bar)
        self.notmem = QtGui.QLabel("", parent.status_bar)
        self.act = QtGui.QLabel("", parent.status_bar)
        parent.clear_status_bar()
        parent.add_to_status_bar(self.sched)
        parent.add_to_status_bar(self.notmem)
        parent.add_to_status_bar(self.act)
        parent.status_bar.setSizeGripEnabled(0)

    def determine_stretch_factors(self, q, a):
        q_stretch, a_stretch = 1, 1
        if "img src" in q:
            q_stretch = 2
        if "img src" in a:
            a_stretch = 2
        return q_stretch, a_stretch

    def set_stretch_factors(self):
        q_stretch, a_stretch = self.determine_stretch_factors(\
            self.review_controller().card.question("plain_text"),
            self.review_controller().card.answer("plain_text"))
        self.vertical_layout.setStretchFactor(self.question_box, q_stretch)
        self.vertical_layout.setStretchFactor(self.answer_box, a_stretch)
        
    def show_answer(self):
        self.review_controller().show_answer()

    def grade_answer(self, grade):
        self.review_controller().grade_answer(grade)

    def set_question_box_visible(self, is_visible):
        if is_visible:
            self.question.show()
            self.question_label.show()
        else:
            self.question.hide()
            self.question_label.hide()

    def set_answer_box_visible(self, is_visible):
        if is_visible:
            self.answer.show()
            self.answer_label.show()
        else:
            self.answer.hide()
            self.answer_label.hide()

    def set_question_label(self, text):
        self.question_label.setText(text)

    def set_question(self, text):
        self.set_stretch_factors()
        self.question.setHtml(text)
        
    def set_answer(self, text):
        self.answer.setHtml(text)

    def clear_question(self):
        self.question.setHtml(self._empty)
        
    def clear_answer(self):
        self.answer.setHtml(self._empty)

    def restore_focus(self):
        # After clicking on the question or the answer, that widget grabs the
        # focus, so that the keyboard shortcuts no longer work. This functions
        # is used to set the focus back to the correct widget.
        if self.focus_widget:
            self.focus_widget.setDefault(True)
            self.focus_widget.setFocus()
        
    def update_show_button(self, text, is_default, is_enabled):
        self.show_button.setText(text)
        self.show_button.setEnabled(is_enabled)
        if is_default:
            self.show_button.setDefault(True)
            self.show_button.setFocus()
            self.focus_widget = self.show_button

    def set_grades_enabled(self, is_enabled):
        self.grades.setEnabled(is_enabled)
        
    def set_grade_enabled(self, grade, is_enabled):
        self.grade_buttons.button(grade).setEnabled(is_enabled)
        
    def set_default_grade(self, grade):
        if self.auto_focus_grades:
            # On Windows, we seem to need to clear the previous default
            # first.
            for grade_i in range(6):
                self.grade_buttons.button(grade_i).setDefault(False)
            self.grade_buttons.button(grade).setDefault(True)
            self.grade_buttons.button(grade).setFocus()
            self.focus_widget = self.grade_buttons.button(grade)
 
    def set_grades_title(self, text):
        self.grades.setTitle(text)
        
    def set_grade_text(self, grade, text):
        self.grade_buttons.button(grade).setText(text)
        
    def set_grade_tooltip(self, grade, text):
        self.grade_buttons.button(grade).setToolTip(text)

    def update_status_bar_counters(self):
        scheduled_count, non_memorised_count, active_count = \
            self.review_controller().counters()
        self.sched.setText(_("Scheduled: %d ") % scheduled_count)
        self.notmem.setText(_("Not memorised: %d ") % non_memorised_count)
        self.act.setText(_("Active: %d ") % active_count)

    def redraw_now(self):
        self.repaint()        
        self.parent().repaint()
