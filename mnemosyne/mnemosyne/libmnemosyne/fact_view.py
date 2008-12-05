#
# fact_view.py <Peter.Bienstman@UGent.be>
#


class FactView(object):

    """Sequence of fields from a fact to form a question and an answer.
    A fact view needs an id as well as a name, because the name can
    change for different translations. 
    
    For card types which need a more general mechanism (e.g. cloze deletion), 
    the variable 'extra_data' can be used to store extra information in the 
    database. The approach with the extra variable was chosen as opposed to a 
    conceptually cleaner inheritance of FactView, in order to get easier mapping
    onto an SQL database (in which it could be stored as a pickled object).

    """

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.q_fields = []
        self.a_fields = []
        self.required_fields = []
        self.a_on_top_of_q = False
        self.extra_data = None
