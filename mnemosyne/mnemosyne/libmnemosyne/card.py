#
# card.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component_manager import *


class Card(object):

    """A card is formed when a fact view operates on a fact."""

    def __init__(self, fact, fact_view):

        self.fact = fact
        self.fact_view = fact_view
        self.id = self.fact.id + "." + str(self.fact_view.id)
        self.reset_learning_data()

    def reset_learning_data(self):

        """Used when creating a card for the first time, or when choosing
        'reset learning data' on import.

        Last_rep and next_rep are measured in days since the creation of
        the database. Note that these values should be stored as float in
        SQL to accomodate plugins doing minute-level scheduling.

        Note: self.unseen is needed on top of self.acq_reps, because the
        initial grading of a manually added card is counted as the first
        repetition. An imported card has no such initial grading, and
        therefore we do the initial grading the first time we see it during
        the interactive learning process. Because of this, determining if a
        card has been seen during the interactive learning process can not
        be decided on the basis of acq_reps, but still that information is
        needed when randomly selecting unseen cards to learn.

        """

        db = get_database()
        self.grade = 0
        self.easiness = db.average_easiness()
        self.acq_reps = 0
        self.ret_reps = 0
        self.lapses = 0
        self.acq_reps_since_lapse = 0
        self.ret_reps_since_lapse = 0
        self.last_rep = 0
        self.next_rep = 0
        self.unseen = True

    def set_initial_grade(self, grade):

        """This is called after manually adding cards. This code is separated
        out from the constructor, as for imported for imported cards, there is
        no grading information available when there are created, and the
        initial grading is done the first time they are are seen in
        the interactive review process (by similar code in the scheduler).

        This initial grading is seen as the first repetition.

        """

        db = get_database()
        sch = get_scheduler()
        self.grade = grade
        self.easiness = db.average_easiness()
        self.acq_reps = 1 #
        self.acq_reps_since_lapse = 1 #
        self.last_rep = db.days_since_start() #
        new_interval = sch.calculate_initial_interval(grade) #
        new_interval += sch.calculate_interval_noise(new_interval) #
        self.next_rep = db.days_since_start() + new_interval #

    def question(self):
        card_type = get_card_type_by_id(self.card_type_id)
        q = card_type.generate_q(self.fact, self.fact_view)
        for f in get_card_filters():
            q = f.run(q)
        return q

    def answer(self):
        card_type = get_card_type_by_id(self.card_type_id)
        a = card_type.generate_a(self.fact, self.fact_view)
        for f in get_card_filters():
            a = f.run(a)
        return a

    def interval(self):
        return self.next_rep - self.last_rep

    # TODO: see which of these we still need and if they could be moved to
    # database

    def sort_key(self):
        return self.next_rep

    def sort_key_newest(self):
        return self.acq_reps + self.ret_reps

    def days_since_last_rep(self):
        return days_since_start - self.last_rep

    def days_until_next_rep(self):
        return self.next_rep - days_since_start

    def change_category(self, new_cat_name):
        old_cat = self.cat
        self.cat = get_category_by_name(new_cat_name)
        remove_category_if_unused(old_cat)
