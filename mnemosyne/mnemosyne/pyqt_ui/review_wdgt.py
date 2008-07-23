##############################################################################
#
# Review widget <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_review_wdgt import *

from mnemosyne.libmnemosyne.plugin_manager import get_ui_controller
from mnemosyne.libmnemosyne.config import config



##############################################################################
#
# ReviewWdgettable {margin-left:auto; margin-right:auto; height:100%;}
#
##############################################################################

class ReviewWdgt(QWidget, Ui_ReviewWdgt):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent = None):
        
        QWidget.__init__(self, parent)
        self.setupUi(self)


        self.question.setHtml("""
<html><head>

<style type="text/css">

table { margin-left: auto;
        margin-right: auto; /* Centers the table, but not it's contents. */
        height: 100%; }

body {  color: black;
        background-color: white;
        margin: 0;
        padding: 0;
        border: thin solid #8F8F8F; }

#q { font-weight: bold;
     text-align: center; } /* Align contents within the cell. */
        
#a { color: green;
     text-align: center; }
        
</style></head>
<body><table><tr><td>

<p id='q'>
question
</p>
<p id='a'>
answer
</p>

</td></tr></table></body></html>
""")


        self.controller = get_ui_controller()

        self.card = None # To controller?

        self.grade_buttons = []

        self.grade_buttons.append(self.grade_0_button)
        self.grade_buttons.append(self.grade_1_button)
        self.grade_buttons.append(self.grade_2_button)
        self.grade_buttons.append(self.grade_3_button)
        self.grade_buttons.append(self.grade_4_button)
        self.grade_buttons.append(self.grade_5_button)

        self.controller.new_question()
        self.updateDialog()



    ##########################################################################
    #
    # show_answer
    #
    ##########################################################################

    def show_answer(self):

        self.controller.show_answer() # TODO: update signal/slot



    ##########################################################################
    #
    # gradeAnswer
    #
    ##########################################################################

    def gradeAnswer(self, grade):

        # TODO: optimise by displaying new question before grading the
        # answer, provided the queue contains at least one card.

        interval = self.controller.grade_answer()

        self.newQuestion()
        self.updateDialog()

        if get_config("show_intervals") == "statusbar":
            self.statusbar.message(self.trUtf8("Returns in ").append(\
                str(interval)).append(self.trUtf8(" day(s).")))



    ##########################################################################
    #
    # next_rep_string
    #
    ##########################################################################

    def next_rep_string(self, days):

        if days == 0:
            return QString('\n') + self.trUtf8("Next repetition: today.")
        elif days == 1:
            return QString('\n') + self.trUtf8("Next repetition: tomorrow.")
        else:
            return QString('\n') + self.trUtf8("Next repetition in ").\
                   append(QString(str(days))).\
                   append(self.trUtf8(" days."))


    def set_window_title(self, title):
        self.setWindowTitle(title)

    def enable_edit_current_card(self, enable):
        self.actionEditCurrentCard.setEnabled(enable)

    def enable_delete_current_card(self, enable):
        self.actionDeleteCurrentCard.setEnabled(enable)

    def enable_edit_deck(self, enable):
        self.actionEditDeck.setEnabled(enable)

    def get_font_size(self):
        return font.pointSize()

    def set_question_label(self, text):
        self.question_label.setText(text)

    def set_question(self, text):
        self.question.setText(text)

    def set_answer(self, text):
        self.answer.setText(text)

    def update_show_button(self, text, default, show_enabled):
        self.show_button.setText(text)
        self.show_button.setDefault(default)
        self.show_button.setEnabled(show_enabled)


    ##########################################################################
    #
    # update_dialog
    #
    #   Contains the updating of the dialog that is not specifically
    #   handled by the UI controller.
    #
    ##########################################################################

    def updateDialog(self):

        # TODO: throw this option out?

        # Update toolbar.

        #if config["hide_toolbar"] == True:
        #    self.parent.toolbar.hide()
        #    self.actionShowToolbar.setChecked(0)
        #else:
        #    self.parent.toolbar.show()
        #    self.actionShowToolbar.setChecked(1)

        # Update question and answer font.

        if config["QA_font"] != None:
            font = QFont()
            font.fromString(config["QA_font"])
        else:
            font = self.show_button.font()

        self.question.setFont(font)
        self.answer.setFont(font)

        # Update question and answer alignment.

        # TODO: reimplement

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

