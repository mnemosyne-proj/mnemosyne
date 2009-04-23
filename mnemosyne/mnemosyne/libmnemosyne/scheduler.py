#
# scheduler.py <Peter.Bienstman@UGent.be>
#


class Scheduler(object):

    name = ""

    def reset(self):
        raise NotImplementedError

    def set_initial_grade(self, card, grade):
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

