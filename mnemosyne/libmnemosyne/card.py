#
# card.py <Peter.Bienstman@gmail.com>
#

import time

from mnemosyne.libmnemosyne.utils import CompareOnId
from mnemosyne.libmnemosyne.utils import rand_uuid, numeric_string_cmp_key


class Card(CompareOnId):

    """A card has a question and an answer and also stores repetition data.

    Questions and answers are dynamically generated depending on the card
    type. Different render chains are supported, to e.g. render the question
    for use in the review window, in the card browser, ... .

    Creation and modification dates are POSIX timestamps stored as integers.

    For card types which need extra information (e.g. cloze deletion), the
    variable 'extra_data' can be used to store this extra information in the
    database. It's dictionary which should contain only standard Python
    objects.

    'scheduler_data' is a variable that can be used by a scheduler to save
    state. It is an integer as opposed to a complex datatype to to allow for
    fast sql queries. If a scheduler needs additional data, it can be stored
    in 'extra_data', but then the custom scheduler needs to make sure it
    explicitly logs an 'edited_card' event so that 'extra data' gets sent
    across during sync.

    'active' is used to determine whether a card is included in the review
    process. Currently, the UI allows setting cards as active if they belong to
    certain card type/fact view combos. We choose to store this information on
    card level and not as a flag in fact view or tag, so that plugins have the
    possibility to offer more flexibility, e.g. by having cards active based
    on grade, ...

    'id' is used to identify this object to the external world (logs, xml
    files, sync, ...), whereas '_id' is an internal id that could be different
    and that can be used by the database for efficiency reasons.

    Card types have been designed so as to require minimal typing when creating
    a custom card type, which is why we use class variables. Therefore, when
    creating new cards programatically, we need to take care to overwrite the
    class variables with instance variables.

    """

    def __init__(self, card_type, fact, fact_view, creation_time=None):
        self.card_type = card_type
        self.fact = fact
        self.fact_view = fact_view
        self.id = rand_uuid()
        self._id = None
        if creation_time is None:
            creation_time = int(time.time())
        self.creation_time = creation_time
        self.modification_time = self.creation_time
        self.tags = set()
        self.extra_data = {}
        self.scheduler_data = 0
        self.active = True
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
        a resolution in seconds, they accomodate plugins doing minute-level
        scheduling. Storing them as int makes it very efficient in SQL.

        """

        self.grade = -1
        self.next_rep = -1
        self.last_rep = -1
        self.easiness = 2.5
        self.acq_reps = 0
        self.ret_reps = 0
        self.lapses = 0
        self.acq_reps_since_lapse = 0
        self.ret_reps_since_lapse = 0

    def question(self, render_chain="default", **render_args):
        return self.card_type.render_question\
            (self, render_chain, **render_args)

    def answer(self, render_chain="default", **render_args):
        return self.card_type.render_answer\
            (self, render_chain, **render_args)

    def tag_string(self):
        tag_names = [tag.name for tag in self.tags \
            if tag.name != "__UNTAGGED__"]
        sorted_tag_names = sorted(tag_names, key=numeric_string_cmp_key)
        return ", ".join(sorted_tag_names)

