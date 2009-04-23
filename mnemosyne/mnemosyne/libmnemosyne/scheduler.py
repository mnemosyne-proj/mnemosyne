#
# scheduler.py <Peter.Bienstman@UGent.be>
#


class Scheduler(object):

    name = ""

    def reset(self):
        raise NotImplementedError

    def set_initial_grade(self, card, grade):

        """Called when cards are given their initial grade outside of the
        review process, e.g. when the user gives an initial grade when
        adding a new card in the GUI. Therefore, 'unseen' is still left to
        True, as this card has not yet been seen in the interactive review
        process.

        Cards which don't have initial grade information available (e.g. for
        cards created during import or conversion from different card type),
        get their initial grade when they are encountered in the interactive
        review process for the first time.
        
        In both cases, this initial grading is seen as the first repetition.

        In this way, both types of cards are treated in the same way. (There
        is an ineffectual asymmetry left in the log messages they generate,
        but all the relevant information can still be parsed from them.)

        """
                
        raise NotImplementedError

    def rebuild_queue(self, learn_ahead=False):
        raise NotImplementedError

    def get_next_card(self, learn_ahead=False):
        raise NotImplementedError

    def allow_prefetch(self):

        """Can we display a new card before having processed the grading of
        the previous one?.

        """
        
        raise NotImplementedError    

    def process_answer(self, card, new_grade, dry_run=False):
        raise NotImplementedError

