#
# card.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.utils import CompareOnId


class Card(CompareOnId):

    """A card has a question and an answer, based on a fact view operating on
    a fact. It also stores repetition data.

    For card types which need extra information (e.g. cloze deletion), the
    variable 'extra_data' can be used to store extra information in the
    database. It's dictionary which should contain only standard Python
    objects.

    'scheduler_data' is a variable that can be used by a scheduler to save
    state. It is an integer as opposed to a complex datatype to to allow for
    fast sql queries. If a scheduler needs additional data, it can be stored
    in 'extra_data', but then the custom scheduler needs to make sure it
    explicitly logs an 'updated_card' event so that 'extra data' gets sent
    across during sync.

    'active' is used to determine whether a card is included in the review
    process. Currently, the UI allows setting cards active when then belong to
    certain card type/fact view combos. We choose to store this information on
    card level and not as a flag in fact view or tag, so that plugins have the
    possibility to offer more flexibility, e.g. by having different active
    tags per card type/fact view combo.

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
        self._id = None
        self.tags = set()
        self.extra_data = {}
        self.scheduler_data = 0
        self.active = True
        self.in_view = True
        self.reset_learning_data()
        
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

    def question(self, exporting=False):

        """When 'exporting' is True, filters that have 'run_on_export' set to
        False are not run. 
        
        """
                
        return self.fact.card_type.question(self, exporting)
       
    def answer(self, exporting=False):

        """When 'exporting' is True, filters that have 'run_on_export' set to
        False are not run. 
        
        """
                
        return self.fact.card_type.answer(self, exporting)

    def tag_string(self):
        return ", ".join([tag.name for tag in self.tags])
        
    interval = property(lambda self : self.next_rep - self.last_rep)
