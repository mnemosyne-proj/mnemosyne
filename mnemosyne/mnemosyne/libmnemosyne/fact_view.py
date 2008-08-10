#
# fact_view.py <Peter.Bienstman@UGent.be>
#

from component_manager import get_fact_filters


class FactView(object):

    """Sequence of fields to from a fact to form a question and an answer."""

    def __init__(self, name):
        self.name = name
        self.q_fields = []
        self.a_fields = []
        self.required_fields = []

    def question(self, fact):
        for field in self.q_fields:
            key = field[0]
            s = fact[key]

            for filter in get_fact_filters():
                s = filter.run(s)

            q += "<div id=\"%s\">%s</div>" % key, fact[key]
        return q

    def answer(self, fact):
        for field in self.a_fields:
            key = field[0]
            s = fact[key]

            for filter in get_fact_filters():
                s = filter.run(s)

            a += "<div id=\"%s\">%s</div>" % key, fact[key]
        return a
