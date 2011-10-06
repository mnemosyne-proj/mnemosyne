#
# SM2_controller.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.review_controller import ReviewController

ACQ_PHASE = 0
RET_PHASE = 1

class SM2Controller(ReviewController):

    # Tooltip texts.  The first index deals with whether we have a card with
    # previous grade 0 or 1 (i.e. non memorised).  The second index is the grade.
    tooltip = [["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""]]
    tooltip[ACQ_PHASE][0] = \
        _("You don't remember this card yet.")
    tooltip[ACQ_PHASE][1] = \
        _("Like '0', but it's getting more familiar. Show it less often.")
    tooltip[ACQ_PHASE][2] = \
        _("You've memorised this card now, and might remember it tomorrow.")
    tooltip[ACQ_PHASE][3] = \
        _("You've memorised this card now, and should remember it tomorrow.")
    tooltip[ACQ_PHASE][4] = \
        _("You've memorised this card now, and might remember it in 2 days.")
    tooltip[ACQ_PHASE][5] = \
        _("You've memorised this card now, and should remember it in 2 days.")

    tooltip[RET_PHASE][0]  = \
        _("You've forgotten this card completely.")
    tooltip[RET_PHASE][1] = \
        _("You've forgotten this card.")
    tooltip[RET_PHASE][2] = \
        _("Barely correct answer. The interval was way too long.")
    tooltip[RET_PHASE][3] = \
        _("Correct answer, but with much effort. The interval was probably too long.")
    tooltip[RET_PHASE][4] = \
        _("Correct answer, with some effort. The interval was probably just right.")
    tooltip[RET_PHASE][5] = \
        _("Correct answer, but without any difficulties. The interval was probably too short.")

    def retranslate(self):
        for phase_idx, tiplist in enumerate(self.tooltip):
            for idx, tip in enumerate(self.tooltip[phase_idx]):
                self.tooltip[phase_idx][idx] = _(tip)

    def reset(self):

        """A Plugin can have a new scheduler, a new review controller or both,
        and in order to avoid running this time consuming code more than once,
        it is not folded into 'activate'.

        """

        self.card = None
        self.state = "EMPTY"
        self.learning_ahead = False
        self.non_memorised_count = None
        self.scheduled_count = None
        self.active_count = None
        self.rep_count = 0
        self.widget = self.component_manager.current("review_widget")\
                      (self.component_manager)
        self.widget.activate()
        self.scheduler().reset()
        self.show_new_question()

    def reset_but_try_to_keep_current_card(self):

        """This is typically called after activities which invalidate the
        current queue, like 'Activate cards' or 'Configure'. For the best user
        experience, we try to keep the card that is currently being asked if
        possible.

        """

        sch = self.scheduler()
        sch.reset()
        sch.rebuild_queue()
        self.reload_counters()
        self.update_status_bar_counters()
        # Try to get a new card in case there was previously no card active,
        # or the previous card is no longer in the queue.
        if self.card is None or not sch.is_in_queue(self.card):
            self.show_new_question()
        # Otherwise, it's already being asked and we need to remove it from
        # the queue. For robustness reasons, we also remove the second grade
        # 0 copy if needed.
        else:
            sch.remove_from_queue_if_present(self.card)
            sch.remove_from_queue_if_present(self.card)
            
    def heartbeat(self):

        """To be called several times during the day, to make sure that
        the data gets updated when a new day starts.

        """
        
        self.flush_sync_server() 
        self.reset_but_try_to_keep_current_card()

    def show_new_question(self):
        # Reload the counters if they have not yet been initialised. Also do
        # this if the active counter is zero, make sure it is really zero to
        # get a correct test for no more cards.
        if self.active_count in [None, 0]:
            self.reload_counters()
        if not self.database().is_loaded() or self.active_count == 0:
            self.state = "EMPTY"
            self.card = None
        else:
            self.card = self.scheduler().next_card(self.learning_ahead)
            if self.card is not None:
                self.state = "SELECT SHOW"
            else:
                self.state = "SELECT AHEAD"
        self.update_dialog()
        self.stopwatch().start()

    def show_answer(self):
        if self.state == "SELECT AHEAD":
            self.learning_ahead = True
            self.show_new_question()
        else:
            self.stopwatch().stop()
            self.state = "SELECT GRADE"
        self.update_dialog()

    def grade_answer(self, grade):

        """Note that this also pulls in a new question."""

        self.flush_sync_server()
        card_to_grade = self.card
        old_grade = card_to_grade.grade
        self.update_counters(old_grade, grade)
        self.rep_count += 1
        if self.scheduler().is_prefetch_allowed(card_to_grade):            
            self.show_new_question()
            interval = self.scheduler().grade_answer(card_to_grade, grade)
            self.database().update_card(card_to_grade, repetition_only=True)
            if self.rep_count % self.config()["save_after_n_reps"] == 0:
                self.database().save()
        else:
            interval = self.scheduler().grade_answer(card_to_grade, grade)
            self.database().update_card(card_to_grade, repetition_only=True)
            if self.rep_count % self.config()["save_after_n_reps"] == 0:
                self.database().save()
            self.show_new_question()  
        if self.config()["show_intervals"] == "status_bar":
            import math
            days = int(math.ceil(interval / (24.0 * 60 * 60)))
            self.main_widget().set_status_bar_message(_("Returns in") + \
                " " + str(interval) + _(" day(s)."))
        
    def next_rep_string(self, days):
        if days == 0:
            return '\n' + _("Next repetition: today.")
        elif days == 1:
            return '\n' + _("Next repetition: tomorrow.")
        else:
            return '\n' + _("Next repetition in ") + str(days) + _(" days.")

    def counters(self):
        if self.non_memorised_count is None:
            self.reload_counters()
        return self.scheduled_count, self.non_memorised_count, self.active_count

    def reload_counters(self):
        sch = self.scheduler()
        self.scheduled_count = sch.scheduled_count()
        self.non_memorised_count = sch.non_memorised_count()
        self.active_count = sch.active_count()

    def update_counters(self, old_grade, new_grade):
        if self.scheduled_count is None:
            self.reload_counters()        
        if old_grade >= 2 and not self.learning_ahead:
            self.scheduled_count -= 1
        if old_grade >= 2 and new_grade <= 1:
            self.non_memorised_count += 1
        if old_grade <= 1 and new_grade >= 2: 
            self.non_memorised_count -= 1
            
    def update_dialog(self, redraw_all=False):
        self.update_qa_area(redraw_all)
        self.update_grades_area()
        self.update_status_bar_counters()
        self.update_menu_bar()
        self.widget.redraw_now()  # Don't wait until disk activity dies down.
                   
    def update_qa_area(self, redraw_all=False):
        w = self.widget
        # Hide/show the question and answer boxes.
        if self.state == "SELECT SHOW":
            w.set_question_box_visible(True)
            if self.card.fact_view.a_on_top_of_q:
                w.set_answer_box_visible(False)
        elif self.state == "SELECT GRADE":
            w.set_answer_box_visible(True)
            if self.card.fact_view.a_on_top_of_q:
                w.set_question_box_visible(False)
        else:
            w.set_question_box_visible(True)
            w.set_answer_box_visible(True)
        # Update question label.
        question_label_text = _("Question: ")
        if self.card is not None:
            question_label_text += self.card.tag_string()
        w.set_question_label(question_label_text)
        # Update question content.
        if self.card is None:
            w.clear_question()
        elif self.state == "SELECT SHOW" or redraw_all == True:
            w.set_question(self.card.question(self.render_chain))
        # Update answer content.
        if self.card is None or self.state == "SELECT SHOW":
            w.clear_answer()
        else:
            w.set_answer(self.card.answer(self.render_chain))
        # Update 'Show answer' button.
        if self.state == "EMPTY":
            show_enabled, default, text = False, False, _("Show answer")
            self.grades_enabled = False
        elif self.state == "SELECT SHOW":
            show_enabled, default, text = True,  True, _("Show answer")
            self.grades_enabled = False
        elif self.state == "SELECT GRADE":
            show_enabled, default, text = False, False, _("Show answer")
            self.grades_enabled = True
        elif self.state == "SELECT AHEAD":
            show_enabled, default, text = True,  False, \
                                     _("Learn ahead of schedule")
            self.grades_enabled = False
        w.update_show_button(text, default, show_enabled)

    def update_grades_area(self):
        w = self.widget
        # Update grade buttons.
        if self.card and self.card.grade < 2:
            phase = ACQ_PHASE
            default_grade = 2
        else:
            phase = RET_PHASE
            default_grade = 4
        w.set_grades_enabled(self.grades_enabled)
        if self.grades_enabled:
            w.set_default_grade(default_grade)         
        # Set title for grades box.
        if self.state == "SELECT GRADE" and \
               self.config()["show_intervals"] == "buttons":
            w.set_grades_title(_("Pick days until next repetition:"))
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
                w.set_grade_tooltip(grade, self.tooltip[phase][grade] + \
                    self.next_rep_string(days))
            else:
                w.set_grade_tooltip(grade, self.tooltip[phase][grade])
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

    def update_status_bar_counters(self):
        self.widget.update_status_bar_counters()

    def is_question_showing(self):
        return self.review_controller().state == "SELECT SHOW"

    def is_answer_showing(self):
        return self.review_controller().state == "SELECT GRADE"
