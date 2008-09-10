#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_review_wdgt import *

from mnemosyne.libmnemosyne.component_manager import component_manager, config
from mnemosyne.libmnemosyne.component_manager import ui_controller_review

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

class ReviewWdgt(QWidget, Ui_ReviewWdgt):
    
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.controller = ui_controller_review()
        self.controller.widget = self
        self.grade_buttons = QButtonGroup()
        self.grade_buttons.addButton(self.grade_0_button, 0)
        self.grade_buttons.addButton(self.grade_1_button, 1)
        self.grade_buttons.addButton(self.grade_2_button, 2)
        self.grade_buttons.addButton(self.grade_3_button, 3)
        self.grade_buttons.addButton(self.grade_4_button, 4)
        self.grade_buttons.addButton(self.grade_5_button, 5)
        self.connect(self.grade_buttons, SIGNAL("buttonClicked(int)"),\
                    self.grade_answer)
        self.controller.new_question()

    def show_answer(self):
        self.controller.show_answer()

    def grade_answer(self, grade):
        self.controller.grade_answer(grade)

    def set_window_title(self, title):
        self.setWindowTitle(title)

    # TODO: pass on to parent
    
    def enable_edit_current_card(self, enable):
        return
        self.actionEditCurrentCard.setEnabled(enable)

    def enable_delete_current_card(self, enable):
        return        
        self.actionDeleteCurrentCard.setEnabled(enable)

    def enable_edit_deck(self, enable):
        return        
        self.actionEditDeck.setEnabled(enable)

    def get_font_size(self):
        return font.pointSize()

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
        self.show_button.setText(text)
        self.show_button.setDefault(default)
        self.show_button.setEnabled(show_enabled)

    def question_box_visible(self, visible):
        if visible:
            self.question.show()
            self.question_label.show()
        else:
            self.question.hide()
            self.quesion_label.hide()            

    def answer_box_visible(self, visible):
        if visible:
            self.answer.show()
            self.answer_label.show()
        else:
            self.answer.hide()
            self.quesion_label.hide()

    # TODO: implement

    def grade_4_default(self, use_4):

        return

        # Revert to blank slate.
        
        self.grade_0_button.setDefault(False)
        self.grade_4_button.setDefault(False)

        self.disconnect(self.defaultAction,SIGNAL("activated()"),
                        self.grade_0_button.animateClick)
        
        self.disconnect(self.defaultAction,SIGNAL("activated()"),
                        self.grade_4_button.animateClick)

        if use_4:
            self.grade_4_button.setDefault(grades_enabled)
            self.connect(self.actionDefault,SIGNAL("activated()"),
                         self.grade_4_button.animateClick)
        else:
            self.grade_0_button.setDefault(grades_enabled)
            self.connect(self.actionDefault,SIGNAL("activated()"),
                         self.grade_0_button.animateClick)

    def enable_grades(self, grades_enabled):
        self.grades.setEnabled(grades_enabled)
 
    def set_grades_title(self, text):
        self.grades.setTitle(text)
        
    def set_grade_text(self, grade, text):
        self.grade_buttons.button(grade).setText(text)
        
    def set_grade_tooltip(self, grade, text):
        self.grade_buttons.button(grade).setToolTip(text)
  
       
            
    ##########################################################################
    #
    # update_dialog
    #
    #   Contains the updating of the dialog that is not specifically
    #   handled by the UI controller.
    #
    ##########################################################################

    def update_dialog(self):
        # Update question and answer font.

        if config()["QA_font"] != None:
            font = QFont()
            font.fromString(config()["QA_font"])
        else:
            font = self.show_button.font()

        #self.question.setFont(font)
        #self.answer.setFont(font)

        # Update question and answer alignment.

        # TODO: reimplement as a filter, or throw out?

        #if get_config("left_align") == True:
        #    alignment = Qt.AlignAuto    | Qt.AlignVCenter | Qt.TextWordWrap
        #else:
        #    alignment = Qt.AlignHCenter | Qt.AlignVCenter | Qt.TextWordWrap

        #self.question.setAlignment(alignment)
        #self.answer.setAlignment(alignment)

        # Update status bar.


        # TODO: move to main window controller

        #self.sched .setText(self.trUtf8("Scheduled: ").append(QString(\
        #                    str(scheduled_cards()))))
        #self.notmem.setText(self.trUtf8("Not memorised: ").append(QString(\
        #                    str(non_memorised_cards()))))
        #self.all   .setText(self.trUtf8("All: ").append(QString(\
        #                    str(active_cards()))))

        # TODO: autoshrinking?
        #if self.shrink == True:
        #    self.adjustSize()


# Register widget.

component_manager.register("review_widget", ReviewWdgt)
