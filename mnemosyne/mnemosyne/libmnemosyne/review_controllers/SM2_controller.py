#
# SM2_controller.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.review_controller import ReviewController


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


class SM2Controller(ReviewController):

    def activate(self):
        self.reset()
        
    def reset(self):
        self.card = None
        self.state = "EMPTY"
        self.learning_ahead = False
        self.non_memorised_count = None
        self.scheduled_count = None
        self.active_count = None
        self.scheduler().reset()     

    def heartbeat(self):

        """To be called several times during the day, to make sure that
        the data gets updated when a new day starts."""
            
        self.reload_counters()
        self.review_widget().update_status_bar()
        self.scheduler().heartbeat()
        if not self.card or self.learning_ahead:
            self.reset()
            self.new_question()

    def new_question(self):
        if not self.active_count:
            self.reload_counters()
        if not self.database().is_loaded() or self.active_count == 0:
            self.state = "EMPTY"
            self.card = None
        else:
            self.card = self.scheduler().get_next_card(self.learning_ahead)
            if self.card != None:
                self.state = "SELECT SHOW"
            else:
                self.state = "SELECT AHEAD"
        self.update_dialog()
        self.stopwatch().start()

    def show_answer(self):
        if self.state == "SELECT AHEAD":
            self.learning_ahead = True
            self.new_question()
        else:
            self.stopwatch().stop()
            self.state = "SELECT GRADE"
        self.update_dialog()

    def grade_answer(self, grade):
        card_to_grade = self.card
        old_grade = card_to_grade.grade
        self.update_counters(old_grade, grade)
        if self.scheduler().allow_prefetch():
            self.new_question()
            interval = self.scheduler().grade_answer(card_to_grade, grade)
            self.database().update_card(card_to_grade, repetition_only=True)
            self.database().save()
        else:
            interval = self.scheduler().grade_answer(card_to_grade, grade)
            self.database().update_card(card_to_grade, repetition_only=True)
            self.database().save()
            self.new_question()     
        if self.config()["show_intervals"] == "statusbar":
            import math
            days = int(math.ceil(interval / (24.0 * 60 * 60)))
            self.review_widget().update_status_bar(_("Returns in") + " " + \
                  str(interval) + _(" day(s)."))
        
    def next_rep_string(self, days):
        if days == 0:
            return '\n' + _("Next repetition: today.")
        elif days == 1:
            return '\n' + _("Next repetition: tomorrow.")
        else:
            return '\n' + _("Next repetition in ") + str(days) + _(" days.")

    def get_counters(self):
        if not self.non_memorised_count:
            self.reload_counters()
        return self.non_memorised_count, self.scheduled_count, self.active_count

    def reload_counters(self):
        sch = self.scheduler()
        self.non_memorised_count = sch.non_memorised_count()
        self.scheduled_count = sch.scheduled_count()
        self.active_count = sch.active_count()

    def update_counters(self, old_grade, new_grade):
        if not self.scheduled_count:
            self.reload_counters()        
        if old_grade >= 2:
            self.scheduled_count -= 1
        if old_grade >= 2 and new_grade <= 1:
            self.non_memorised_count += 1
        if old_grade <= 1 and new_grade >= 2:
            self.non_memorised_count -= 1
            
    def update_dialog(self, redraw_all=False):
        self.update_qa_area(redraw_all)
        self.update_grades_area()
        self.review_widget().update_status_bar()
        self.update_menu_bar()
                   
    def update_qa_area(self, redraw_all=False):
        w = self.review_widget()
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
        if self.card is not None:
            question_label_text += self.card.tag_string()
        w.set_question_label(question_label_text)
        # Update question content.
        if self.card is None:
            w.clear_question()
        elif self.state == "SELECT SHOW" or redraw_all == True:
            w.set_question(self.card.question())
        # Update answer content.
        if self.card is None or self.state == "SELECT SHOW":
            w.clear_answer()
        else:
            w.set_answer(self.card.answer())
        # Update 'Show answer' button.
        if self.state == "EMPTY":
            show_enabled, default, text = False, True, _("Show answer")
            self.grades_enabled = False
        elif self.state == "SELECT SHOW":
            show_enabled, default, text = True,  True, _("Show answer")
            self.grades_enabled = False
        elif self.state == "SELECT GRADE":
            show_enabled, default, text = False, True, _("Show answer")
            self.grades_enabled = True
        elif self.state == "SELECT AHEAD":
            show_enabled, default, text = True,  False, \
                                     _("Learn ahead of schedule")
            self.grades_enabled = False
        w.update_show_button(text, default, show_enabled)

    def update_grades_area(self):
        w = self.review_widget()
        # Update grade buttons.
        if self.card and self.card.grade < 2:
            i = 0 # Acquisition phase.
            default_grade = 0
            for grade in [3, 4, 5]:
                w.enable_grade(grade, False)
        else:
            i = 1 # Retention phase.
            default_grade = 4
            for grade in [3, 4, 5]:
                w.enable_grade(grade, True)
        w.enable_grades(self.grades_enabled)
        if self.grades_enabled:
            w.set_default_grade(default_grade)         
        # Set title for grades box.
        if self.state == "SELECT GRADE" and \
               self.config()["show_intervals"] == "buttons":
            w.set_grades_title(_("Pick days until next repetition:"))
        else:
            if self.card and self.card.grade == -1:
                w.set_grades_title(_("Select initial grade:"))
            else:
                w.set_grades_title(_("Grade your answer:"))   
        # Set tooltips and texts for the grade buttons.
        for grade in range(0,6):
            # Tooltip.
            if self.state == "SELECT GRADE" and \
               self.config()["show_intervals"] == "tooltips":
                import math
                interval = self.scheduler().process_answer(self.card, \
                    grade, dry_run=True)
                days = int(math.ceil(interval / (24.0 * 60 * 60)))               
                w.set_grade_tooltip(grade, tooltip[i][grade] + \
                    self.next_rep_string(days))
            else:
                w.set_grade_tooltip(grade, tooltip[i][grade])
            # Button text.
            if self.state == "SELECT GRADE" and \
               self.config()["show_intervals"] == "buttons":
                w.set_grade_text(grade, str(self.scheduler().process_answer(\
                                            self.card, grade, dry_run=True)))
            else:
                w.set_grade_text(grade, str(grade))           

    def update_menu_bar(self):
        w = self.main_widget()
        if self.config()["only_editable_when_answer_shown"] == True:
            if self.card and self.state == "SELECT GRADE":
                w.enable_edit_current_card(True)
            else:
                w.enable_edit_current_card(False)
        else:
            if self.card:
                w.enable_edit_current_card(True)
            else:
                w.enable_edit_current_card(False)
        w.enable_delete_current_card(self.card != None)
        w.enable_browse_cards(self.database().is_loaded())

    def is_question_showing(self):
        return self.review_controller().state == "SELECT SHOW"

    def is_answer_showing(self):
        return self.review_controller().state == "SELECT GRADE"
