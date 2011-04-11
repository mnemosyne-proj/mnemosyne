#
# fact_view.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.utils import CompareOnId


class FactView(CompareOnId):

    """Sequence of fields from a fact to form a question and an answer.
    A fact view needs an id string as well as a name, because the name can
    change for different translations.

    Note that id's should be unique to distinguish them during sync, so a
    good naming convention is 'card_type_id.fact_view_id'. (We don't use
    '::' so as not to interfere with the '::' in inherited card types.)

    The purpose of the decorator dictionaries is to allow for cards that read
    'What is the answer to $question', as opposed to just '$question'.
    
    """

    def __init__(self, name, id):
        self.id = id
        self._id = None
        self.name = name
        self.q_fields = []
        self.a_fields = []
        self.q_field_decorators = {}  # {field: string.Template}
        self.a_field_decorators = {}  # {field: string.Template}
        self.a_on_top_of_q = False
        self.type_answer = False
        self.extra_data = {}
