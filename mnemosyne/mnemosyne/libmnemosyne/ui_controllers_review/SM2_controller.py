#
# SM2_controller.py <Peter.Bienstman@UGent.be>
#

import os

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.stopwatch import stopwatch
from mnemosyne.libmnemosyne.component_manager import database, config
from mnemosyne.libmnemosyne.component_manager import scheduler
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.ui_controller_review import UiControllerReview


# Tooltip texts.  The first index deals with whether we have a card with
# previous grade 0 or 1 (i.e. unmemorised).  The second index is the grade.
tooltip = [["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""]]
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
        UiControllerReview.__init__(self)

    def clear(self):
        self.state = "EMPTY"
        self.card = None        

    def new_question(self, learn_ahead=False):
        if database().card_count() == 0:
            self.state = "EMPTY"
            self.card = None
        else:
            self.card = scheduler().get_next_card(learn_ahead)         
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
        interval = scheduler().process_answer(self.card, grade)
        self.new_question()
        if config()["show_intervals"] == "statusbar":
            self.widget.update_sta(_("Returns in") + " " + \
                  str(interval) + _(" day(s)."))
        
    def next_rep_string(self, days):
        if days == 0:
            return '\n' + _("Next repetition: today.")
        elif days == 1:
            return '\n' + _("Next repetition: tomorrow.")
        else:
            return '\n' + _("Next repetition in ") + str(days) + _(" days.")
                   
    def update_dialog(self, redraw_all=False):
        w = self.widget
        if not w:
            return
        # Update title.
        database_name = os.path.basename(config()["path"]).\
            split(database().suffix)[0]
        title = _("Mnemosyne")
        if database_name != _("default"):
            title += " - " + database_name
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
            if self.card.fact_view.a_on_top_of_q:
                w.answer_box_visible(False)
        elif self.state == "SELECT GRADE":
            w.answer_box_visible(True)
            if self.card.fact_view.a_on_top_of_q:
                w.question_box_visible(False)
        else:
            w.question_box_visible(True)
            w.answer_box_visible(True)
        # Update question label.
        question_label_text = _("Question: ")
        if self.card != None and self.card.categories[0].name \
               != _("<default>"):
            for c in self.card.categories:
                question_label_text += c.name + ", "
            question_label_text = question_label_text[:-2]
        w.set_question_label(question_label_text)
        # Update question content.
        if self.card == None:
            w.clear_question()
        elif self.state == "SELECT SHOW" or redraw_all == True:
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
        w.enable_grades(grades_enabled)
        if grades_enabled:
            w.grade_4_default(default_4)            
        # Tooltips and texts for the grade buttons.
        for grade in range(0,6):
            # Tooltip.
            if self.state == "SELECT GRADE" and \
               config()["show_intervals"] == "tooltips":
                w.set_grade_tooltip(grade, tooltip[i][grade] +\
                    self.next_rep_string(scheduler().process_answer(self.card, \
                                        grade, dry_run=True)))
            else:
                w.set_grade_tooltip(grade, tooltip[i][grade])
            # Button text.
            if self.state == "SELECT GRADE" and \
               config()["show_intervals"] == "buttons":
                w.set_grade_text(grade, str(scheduler().process_answer(\
                                            self.card, grade, dry_run=True)))
                w.set_grades_title(_("Pick days until next repetition:"))
            else:
                w.set_grade_text(grade, str(grade))
                w.set_grades_title(_("Grade your answer:"))
            # TODO: accelerator update needed?
            #self.grade_buttons[grade].setAccel(QKeySequence(str(grade)))
        # Update status bar.
        ui_controller_main().widget.update_status_bar()
