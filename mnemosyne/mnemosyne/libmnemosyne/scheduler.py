#
# scheduler.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Scheduler(Component):

    name = ""
    component_type = "scheduler"

    def reset(self):

        """Called when starting the scheduler for the first time."""

        raise NotImplementedError

    def set_initial_grade(self, cards, grade):

        """Sets the initial grades for a set of sister cards, making sure
        their next repetitions do no fall on the same day.

        Called when cards are given their initial grade outside of the
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

    def avoid_sister_cards(self, card):

        """Change card.next_rep to make sure that the card is not scheduled
        on the same day as a sister card.

        Factored out here to allow this to be used by e.g. MnemoGogo.

        """

        raise NotImplementedError

    def rebuild_queue(self, learn_ahead=False):

        """Called by the rest of the library when an existing queue risks
        becoming invalid, e.g. when cards have been deleted in the GUI.
        'next_card' also makes use of this in certain implementations.

        """

        raise NotImplementedError

    def is_in_queue(self, card):

        """To check whether the queue needs to be rebuilt, e.g. if it contains
        a card that was deleted in the GUI.

        """

        raise NotImplementedError

    def remove_from_queue_if_present(self, card):
        raise NotImplementedError

    def next_card(self, learn_ahead=False):
        raise NotImplementedError

    def is_prefetch_allowed(self):

        """Can we display a new card before having processed the grading of
        the previous one?

        """

        raise NotImplementedError

    def grade_answer(self, card, new_grade, dry_run=False):
        raise NotImplementedError

    def scheduled_count(self):
        raise NotImplementedError

    def non_memorised_count(self):
        raise NotImplementedError

    def active_count(self):
        raise NotImplementedError

    def card_count_scheduled_n_days_from_now(self, n):

        """Yesterday: n=-1, today: n=0, tomorrow: n=1, ... .

        Is not implemented in the database, because this could need internal
        scheduler information.
        """

        raise NotImplementedError

    def next_rep_to_interval_string(self, next_rep, now=None):

        """Converts next_rep to a string like 'tomorrow', 'in 2 weeks', ...

        """

        raise NotImplementedError

    def last_rep_to_interval_string(self, last_rep, now=None):

        """Converts last_rep to a string like 'yesterday', '2 weeks ago', ...

        """

        raise NotImplementedError
