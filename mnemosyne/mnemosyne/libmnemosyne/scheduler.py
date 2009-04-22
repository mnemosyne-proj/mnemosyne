#
# scheduler.py <Peter.Bienstman@UGent.be>
#


class Scheduler(object):

    name = ""

    def set_initial_grade(self, card, grade):
        raise NotImplementedError

    def rebuild_queue(self, learn_ahead=False):
        raise NotImplementedError

    def get_next_card(self, learn_ahead=False):
        raise NotImplementedError

    def process_answer(self, card, new_grade, dry_run=False):
        raise NotImplementedError

    def clear_queue(self):
        raise NotImplementedError
