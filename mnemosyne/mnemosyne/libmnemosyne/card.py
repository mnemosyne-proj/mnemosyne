#
# card.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import scheduler


class Card(object):

    """A card is formed when a fact view operates on a fact."""

    def __init__(self, fact, fact_view):
        self.fact = fact
        self.fact_view = fact_view
        self.id = self.fact.uid + "." + str(self.fact_view.id)
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

        self.grade = 0
        self.easiness = database().average_easiness()
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

        db = database()
        sch = scheduler()
        self.grade = grade
        self.easiness = db.average_easiness()
        self.acq_reps = 1
        self.acq_reps_since_lapse = 1
        self.last_rep = db.days_since_start()
        new_interval = sch.calculate_initial_interval(grade)
        new_interval += sch.calculate_interval_noise(new_interval)
        self.next_rep = db.days_since_start() + new_interval

    def question(self):
        return self.fact.card_type.get_renderer().render_card_fields(self, \
                self.fact_view.q_fields)

    def answer(self):
        return self.fact.card_type.get_renderer().render_card_fields(self, \
                self.fact_view.a_fields)
        
    interval = property(lambda self : self.next_rep - self.last_rep)
    
    days_since_last_rep = property(lambda self : \
                            database().days_since_start - self.last_rep)
                            
    days_until_next_rep = property(lambda self : \
                            self.next_rep - database().days_since_start)


