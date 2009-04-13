#
# card.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import scheduler


class Card(object):

    """A card is formed when a fact view operates on a fact.

    For card types which need extra information per card to build their views,
    (e.g. cloze deletion), the variable 'extra_data' can be used to store
    extra information in the database. The approach with the extra variable
    was chosen as opposed to a conceptually cleaner inheritance of FactView,
    in order to get easier mapping onto a database.

    'seen_in_this_session' is a variable used by the scheduler to save state.
    ('session' is not the time the user has the program open, but is rather
    one pass through the entire scheduler algorithmn.)

    'active' is used to determine whether a card is included in the review
    process. Currently, the UI allows setting cards active when then belong to
    certain card type/fact view combos, and when any of their categories are
    considered active. We choose to store this information on card level and
    not as a flag in fact view or category, so that plugins have the
    possibility to offer more flexibility, e.g. by having different active
    categories per card type/fact view combo.

    'in_view' offers similar functionality as 'active', but is not used by the
    scheduler, but e.g. by GUI elements which need to operate only on a subset
    of the cards (displaying search results, e.g.). The 'active' flag could
    serve double duty to store this info, but having a separate flag for this
    is safer.

    """

    def __init__(self, fact, fact_view):
        self.fact = fact
        self.fact_view = fact_view
        self.id = self.fact.id + "." + str(self.fact.card_type.id) + "." + \
                  str(self.fact_view.id)
        self.categories = []
        self.unseen = True
        self.extra_data = ""
        self.seen_in_this_session = False
        self.needs_sync = True
        self.active = True
        self.in_view = True
        self.reset_learning_data()
        
    def __eq__(self, other):                                            
        try:                                                            
            return self.id == other.id                                  
        except:                                                         
            return False

    def reset_learning_data(self):

        """Used when creating a card for the first time, or when choosing
        'reset learning data' on import.

        'last_rep' and 'next_rep' are measured in days since the creation of
        the database. Note that these values should be stored as float in
        order to accomodate plugins doing minute-level scheduling.

        'unseen' means that the card has not been seen during the interactive
        review process. TODO: replace this by grade = -1, or
        grade = 1/0 and acq_reps = 1

        """

        self.grade = -1
        # We need to set this to a sensible value, so as not to upset      
        # future calss to average_easiness. 
        self.easiness = database().average_easiness()
        self.acq_reps = 0
        self.ret_reps = 0
        self.lapses = 0
        self.acq_reps_since_lapse = 0
        self.ret_reps_since_lapse = 0
        self.last_rep = -1
        self.next_rep = -1

    def do_first_rep(self, grade):

        """The first repetition is treated differently, and gives longer
        intervals, to allow for the fact that the user may have seen this
        card before. It is called either directly after adding cards manually
        using the grade specified there, or, for cards which have been created
        during import or from conversion from different card types, during the
        active revies process when they are encountered for the first time.
        In both cases, this initial grading is seen as the first repetition.

        """

        scheduler().do_first_rep(self, grade)

    def question(self):
        return self.fact.card_type.question(self)

    def answer(self):        
        return self.fact.card_type.answer(self)
        
    interval = property(lambda self : self.next_rep - self.last_rep)
    
    days_since_last_rep = property(lambda self : \
                            database().days_since_start - self.last_rep)
                            
    days_until_next_rep = property(lambda self : \
                            self.next_rep - database().days_since_start)


