#
# fact_view.py <Peter.Bienstman@UGent.be>
#

from component_manager import get_fact_filters


class FactView(object):

    """Sequence of fields to from a fact to form a question and an answer.
    A fact view needs an id as well as a name, because the name can
    change for different translations.

    """

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.q_fields = []
        self.a_fields = []
        self.required_fields = []

    def question(self, fact):
        q = ""
        for field in self.q_fields:
            key = field[0]
            s = fact[key]
            for f in get_fact_filters():
                s = f.run(s,  fact)
            q += "<div id=\"%s\">%s</div>" % (key, fact[key])
        return q

    def answer(self, fact):
        a = ""
        for field in self.a_fields:
            key = field[0]
            s = fact[key]
            for f in get_fact_filters():
                s = f.run(s,  fact)
            a += "<div id=\"%s\">%s</div>" % (key, fact[key])
        return a
