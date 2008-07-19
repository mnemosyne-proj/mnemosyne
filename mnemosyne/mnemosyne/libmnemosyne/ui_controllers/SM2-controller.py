##############################################################################
#
# SM2-controller.py <Peter.Bienstman@UGent.be>
#
##############################################################################




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
