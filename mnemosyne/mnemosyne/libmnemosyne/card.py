#
# card.py <Peter.Bienstman@UGent.be>
#

import time


class Card(object):

    """A card has a question and an answer, based on a fact view operating on
    a fact. It also stores repetition data.

    For card types which need extra information (e.g. cloze deletion), the
    variable 'extra_data' can be used to store extra information in the
    database. It's dictionary which should contain only standard Python
    objects.

    'scheduler_data' is a variable that can be used by a scheduler to save
    state.

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

    'id' is used to identify this object to the external world (logs, xml
    files, ...), whereas '_id' is an internal id that could be different and
    that can be used by the database for efficiency reasons.

    """

    def __init__(self, fact, fact_view):
        self.fact = fact
        self.fact_view = fact_view
        self.id = self.fact.id + "." + self.fact.card_type.id + "." + \
                  self.fact_view.id
        self.id_ = None
        self.categories = []
        self.extra_data = {}
        self.scheduler_data = 0
        self.active = True
        self.in_view = True
        self.type_answer = False
        self.reset_learning_data()
        
    def __eq__(self, other):                                            
        try:                                                            
            return self.id == other.id                                  
        except:                                                         
            return False

    def reset_learning_data(self):

        """Used when creating a card for the first time, or when choosing
        'reset learning data' on import.

        'acq_reps' and 'ret_reps' are the number of repetitions this card has
        seen in the acquisition phase (grade 0 and 1) and the retention phase
        (grades 3 through 5) respectively.

        'lapses' is the number of times a card with grade 2 or higher was
        forgotten, i.e. graded 0 or 1.

        'last_rep' and 'next_rep' are integer POSIX timestamps. Since they have
        a resolution in seconds, the accomodate plugins doing minute-level
        scheduling. Storing them as int makes it very efficient in SQL.

        'unseen' means that the card has not been seen during the interactive
        review process. This variable is needed to determine which new cards to
        pull in after current cards have been memorised. These unseen cards have
        two distinct origins: cards that were created interactively by the user
        and given an intial grade 0 or 1 in the 'Add cards' dialog, or cards
        which were created on import or when converting cards types, and which
        yet have to get their initial grade. The first category initially has
        'grade'=0 or 1, and 'ack_reps'=1, and the second category 'grade'=-1
        and 'ack_reps'=0. However, after a subsequent review of a card from the
        second category, its 'grade' and 'ack_reps' could become identical to
        an unseen card in the first category, even though the card is no longer
        unseen. Therefore, just relying on 'grade' and 'ack_reps' to track
        unseen cards does not work.

        """

        self.grade = -1
        self.easiness = -1
        self.acq_reps = 0
        self.ret_reps = 0
        self.lapses = 0
        self.acq_reps_since_lapse = 0
        self.ret_reps_since_lapse = 0
        self.last_rep = -1
        self.next_rep = -1
        self.unseen = True

    def question(self):
        return self.fact.card_type.question(self)

    def answer(self):        
        return self.fact.card_type.answer(self)
        
    interval = property(lambda self : self.next_rep - self.last_rep)
    
    days_since_last_rep = property(lambda self : \
        24 * 60 * 60 * (time.time()  - self.last_rep))
                            
    days_until_next_rep = property(lambda self : \
        24 * 60 * 60 * (self.next_rep - time.time()))


