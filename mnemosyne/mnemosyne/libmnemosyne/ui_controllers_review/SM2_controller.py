#
# SM2-controller.py <Peter.Bienstman@UGent.be>
#

import os

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.stopwatch import stopwatch
from mnemosyne.libmnemosyne.component_manager import database, config
from mnemosyne.libmnemosyne.component_manager import scheduler
from mnemosyne.libmnemosyne.ui_controller_review import UiControllerReview


##############################################################################
#
# Tooltip texts
#
##############################################################################

tooltip = [["","","","","",""],["","","","","",""]]

def install_tooltip_strings(self):

    global tooltip

    tooltip[0][0] = \
        _("You don't remember this card yet.")
    tooltip[0][1] = \
        _("Like '0', but it's getting more familiar.") + " " + \
        _("Show it less often.")
    tooltip[0][2] = tooltip[0][3] = tooltip[0][4] = tooltip[0][5] = \
        _("You've memorised this card now,") + \
        _(" and will probably remember it for a few days.")

    tooltip[1][0] = tooltip[1][1] = \
        _("You have forgotten this card completely.")
    tooltip[1][2] = \
        _("Barely correct answer. The interval was way too long.")
    tooltip[1][3] = \
        _("Correct answer, but with much effort.") + " " + \
        _("The interval was probably too long.")
    tooltip[1][4] = \
        _("Correct answer, with some effort.") + " " + \
        _("The interval was probably just right.")
    tooltip[1][5] = \
        _("Correct answer, but without any difficulties.") + " " + \
        _("The interval was probably too short.")


class SM2Controller(UiControllerReview):

    def __init__(self):
        UiControllerReview.__init__(self, name="SM2 Controller")

    def new_question(self, learn_ahead=False):
        if database().card_count() == 0:
            self.state = "EMPTY"
            self.card = None
        else:
            self.card = scheduler().get_new_question(learn_ahead)
            if self.card != None:
                self.state = "SELECT SHOW"
            else:
                self.state = "SELECT AHEAD"
        self.update_dialog()
        stopwatch.start()

    def show_answer(self):
        if self.state == "SELECT AHEAD":
            self.new_question(learn_ahead=True)
        else:
            stopwatch.stop()
            self.state = "SELECT GRADE"
        self.update_dialog()

    def grade_answer(self, grade):
        # TODO: optimise by displaying new question before grading the
        # answer, provided the queue contains at least one card.
        interval = scheduler().process_answer(self.card, grade)
        self.new_question()
        # TODO: implement
        #if config()["show_intervals"] == "statusbar":
        #    self.statusBar().message(_("Returns in") + " " + \
        #                             str(interval) + _(" day(s)."))

    def update_dialog(self):
        w = self.widget
        # Update title.
        database_name = os.path.basename(config()["path"])[:-4]
        title = _("Mnemosyne") + " - " + database_name
        w.set_window_title(title)
        # Update menu bar.
        if config()["only_editable_when_answer_shown"] == True:
            if self.card != None and self.state == "SELECT GRADE":
                w.enable_edit_current_card(True)
            else:
                w.enable_edit_current_card(False)
        else:
            if self.card != None:
                w.enable_edit_current_card(True)
            else:
                w.enable_edit_current_card(False)
        w.enable_delete_current_card(self.card != None)
        w.enable_edit_deck(database().card_count() > 0)
        # Hide/show the question and answer boxes.
        if self.state == "SELECT SHOW":
            w.question_box_visible(True)
            if self.card.fact.card_type.a_on_top_of_q:
                w.answer_box_visible(False)
        elif self.state == "SELECT GRADE":
            w.answer_box_visible(True)
            if self.card.fact.card_type.a_on_top_of_q:
                w.question_box_visible(False)
        else:
            w.question_box_visible(True)
            w.answer_box_visible(True)
        # Update question label.
        question_label_text = _("Question:")
        if self.card != None and self.card.fact.cat[0].name != _("<default>"):
            for c in self.card.fact.cat:
                question_label_text += " " + c.name
        w.set_question_label(question_label_text)
        # TODO: optimisation to make sure that this does not run several
        # times during card display. People expect there custom filters
        # to run only once if they have side effects...
        # Update question content.
        if self.card == None:
            w.clear_question()
        else:
            w.set_question(self.card.question())
        # Update answer content.
        if self.card == None or self.state == "SELECT SHOW":
            w.clear_answer()
        else:
            w.set_answer(self.card.answer())
        # Update 'Show answer' button.
        if self.state == "EMPTY":
            show_enabled, default, text = False, True, _("Show answer")
            grades_enabled = False
        elif self.state == "SELECT SHOW":
            show_enabled, default, text = True,  True, _("Show answer")
            grades_enabled = False
        elif self.state == "SELECT GRADE":
            show_enabled, default, text = False, True, _("Show answer")
            grades_enabled = True
        elif self.state == "SELECT AHEAD":
            show_enabled, default, text = True,  False, \
                                     _("Learn ahead of schedule")
            grades_enabled = False
        w.update_show_button(text, default, show_enabled)
        # Update grade buttons.
        if self.card != None and self.card.grade in [0,1]:
            i = 0 # Acquisition phase.
            default_4 = False
        else:
            i = 1 # Retention phase.
            default_4 = True
        w.grade_4_default(default_4)
        w.enable_grades(grades_enabled)
        # Run possible update code that independent of the controller state.
        w.update_dialog()
        return
        # Tooltips: TODO
        #QToolTip.setWakeUpDelay(0) #TODO?
        for grade in range(0,6):
            # Tooltip.
            #QToolTip.remove(self.grade_buttons[grade])
            if self.state == "SELECT GRADE" and \
               config()["show_intervals"] == "tooltips":
                self.grade_buttons[grade].setToolTip(tooltip[i][grade].
                      append(self.next_rep_string(process_answer(self.card,
                                                  grade, dry_run=True))))
            else:
                self.grade_buttons[grade].setToolTip(tooltip[i][grade])
            # Button text.
            if self.state == "SELECT GRADE" and \
               config()["show_intervals"] == "buttons":
                self.grade_buttons[grade].setText(\
                        str(process_answer(self.card, grade, dry_run=True)))
                self.grades.setTitle(\
                    _("Pick days until next repetition:"))
            else:
                self.grade_buttons[grade].setText(str(grade))
                self.grades.setTitle(_("Grade your answer:"))
            # TODO: accelerator update needed?
            #self.grade_buttons[grade].setAccel(QKeySequence(str(grade)))
        # Run possible update code that independent of the controller state.
        #w.update_dialog()

