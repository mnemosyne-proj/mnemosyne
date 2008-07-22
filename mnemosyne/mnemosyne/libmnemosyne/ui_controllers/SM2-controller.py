##############################################################################
#
# SM2-controller.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext



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
    


##############################################################################
#
# SM2Controller
#
##############################################################################

class SM2Controller(object):


    ##########################################################################
    #
    # new_question
    #
    ##########################################################################

    def new_question(self, learn_ahead = False):
        
        if number_of_cards() == 0:
            self.state = "EMPTY"
            self.card = None
        else:
            self.card = get_new_question(learn_ahead)
            if self.card != None:
                self.state = "SELECT SHOW"
            else:
                self.state = "SELECT AHEAD"

        #self.q_sound_played = False
        #self.a_sound_played = False
        
        start_thinking()


    ##########################################################################
    #
    # show_answer
    #
    ##########################################################################

    def show_answer(self):

        if self.state == "SELECT AHEAD":
            self.newQuestion(learn_ahead = True)
        else:
            stop_thinking()
            self.state = "SELECT GRADE"
            
        self.widget.updateDialog()


    ##########################################################################
    #
    # grade_answer
    #
    ##########################################################################

    def grade_answer(self, grade):

        interval = process_answer(self.card, grade)

        # Possible optimisation: show new question before grading the
        # answer, but only if the revision queue contains enough cards.

        
    ##########################################################################
    #
    # update_dialog
    #
    ##########################################################################

    def update_dialog(self):

        # Update title.
        
        database_name = os.path.basename(config["path"])[:-4]
        title = _("Mnemosyne") + " - " + database_name
        self.widget.set_window_title(title)

        # Update menu bar.

        if config["only_editable_when_answer_shown"] == True:
            if self.card != None and self.state == "SELECT GRADE":
                self.widget.enable_edit_current_card(True)
            else:
                self.widget.enable_edit_current_card(False)
        else:
            if self.card != None:
                self.widget.enable_edit_current_card(True)
            else:
                self.widget.enable_edit_current_card(False)            
            
        self.widget.enable_delete_current_card(self.card != None)
        self.widget_enable_edit_deck(number_of_cards() > 0)
        
        # Size for non-latin characters.

        increase_non_latin = config["non_latin_font_size_increase"]
        non_latin_size = self.widget.get_font_size() + increase_non_latin

        # Hide/show the question and answer boxes.
        
        if self.state == "SELECT SHOW":
            self.question.show()
            self.question_label.show()
            if self.card.type.a_on_top_of_q == True:
                self.answer.hide()
                self.answer_label.hide()
        elif self.state == "SELECT GRADE":
            self.answer.show()
            self.answer_label.show()
            if self.card.type.a_on_top_of_q == True:
                self.question.hide()
                self.question_label.hide()
        else:
            self.question.show()
            self.question_label.show()
            self.answer.show()
            self.answer_label.show()

        # Update question label.
        
        question_label_text = _("Question:")
        if self.card != None and self.card.cat.name != _("<default>"):
            question_label_text += " " + self.card.cat.name
            
        self.widget.set_question_label(question_label_text)

        # Update question content.
        
        if self.card == None:
            self.widget.set_question("")
        else:
            text = self.card.filtered_q()

            #if self.q_sound_played == False:
            #    play_sound(text)
            #    self.q_sound_played = True
                
            if increase_non_latin:
                text = set_non_latin_font_size(text, non_latin_size)

            self.widget.set_question(text)

        # Update answer content.
        
        if self.card == None or self.state == "SELECT SHOW":
            self.widget.set_answer("")
        else:
            text = self.card.filtered_a()

            #if self.a_sound_played == False:
            #    play_sound(text)
            #    self.a_sound_played = True
                
            if increase_non_latin:
                text = set_non_latin_font_size(text, non_latin_size)

            self.widget.set_answer(text)

        # Update 'show answer' button.
        
        if self.state == "EMPTY":
            show_enabled, default, text = 0, 1, _("Show answer")
            grades_enabled = 0 
        elif self.state == "SELECT SHOW":
            show_enabled, default, text = 1, 1, _("Show answer")
            grades_enabled = 0
        elif self.state == "SELECT GRADE":
            show_enabled, default, text = 0, 1, _("Show answer")
            grades_enabled = 1
        elif self.state == "SELECT AHEAD":
            show_enabled, default, text = 1, 0, \
                                     _("Learn ahead of schedule")
            grades_enabled = 0

        self.widget.update_show_button(text, default, enabled)

        # Update grade buttons. Make sure that no signals get connected
        # twice, and put the disconnects inside a try statement to work
        # around a Windows issue.

        self.grade_0_button.setDefault(False)
        self.grade_4_button.setDefault(False)

        try:
            self.disconnect(self.defaultAction,SIGNAL("activated()"),
                            self.grade_0_button.animateClick)
        except:
            pass
        
        try:
            self.disconnect(self.defaultAction,SIGNAL("activated()"),
                            self.grade_4_button.animateClick)
        except:
            pass
        
        if self.card != None and self.card.grade in [0,1]:  ##
            i = 0 # Acquisition phase.
            self.grade_0_button.setDefault(grades_enabled)
            self.connect(self.actionDefault,SIGNAL("activated()"),
                         self.grade_0_button.animateClick)
        else:
            i = 1 # Retention phase.
            self.grade_4_button.setDefault(grades_enabled)
            self.connect(self.actionDefault,SIGNAL("activated()"),
                         self.grade_4_button.animateClick)
                        
        self.grades.setEnabled(grades_enabled)

        #QToolTip.setWakeUpDelay(0) #TODO?

        for grade in range(0,6):

            # Tooltip.
            
            #QToolTip.remove(self.grade_buttons[grade])
            
            if self.state == "SELECT GRADE" and \
               config["show_intervals"] == "tooltips":
                #QToolTip.add(self.grade_buttons[grade],
                #      tooltip[i][grade].
                #      append(self.next_rep_string(process_answer(self.card,
                #                                  grade, dry_run=True))))
                self.grade_buttons[grade].setToolTip(tooltip[i][grade].
                      append(self.next_rep_string(process_answer(self.card,
                                                  grade, dry_run=True))))
            else:
                self.grade_buttons[grade].setToolTip(tooltip[i][grade])
                
                #QToolTip.add(self.grade_buttons[grade], tooltip[i][grade])

            # Button text.
                    
            if self.state == "SELECT GRADE" and \
               config["show_intervals"] == "buttons":
                self.grade_buttons[grade].setText(\
                        str(process_answer(self.card, grade, dry_run=True)))
                self.grades.setTitle(\
                    _("Pick days until next repetition:"))
            else:
                self.grade_buttons[grade].setText(str(grade))
                self.grades.setTitle(_("Grade your answer:"))

            # Todo: accelerator update needed?
            #self.grade_buttons[grade].setAccel(QKeySequence(str(grade)))

        # Run possible update code that independent of the controller state.

        self.widget.update_dialog()
        
