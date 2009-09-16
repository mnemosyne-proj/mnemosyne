#
# fact_view.py <Peter.Bienstman@UGent.be>
#

class FactView(object):

    # Note: we don't inherit from CompareOnId here, as fact_view.ids are not
    # unique.

    """Sequence of fields from a fact to form a question and an answer.
    A fact view needs an id string as well as a name, because the name can
    change for different translations. 
    
    """

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.q_fields = []
        self.a_fields = []
        self.a_on_top_of_q = False
        self.type_answer = False
        self.extra_data = {}

    
