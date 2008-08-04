##############################################################################
#
# fact_view.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from component_manager import get_fact_filters



##############################################################################
#
# FactView
#
#   A fact view is a sequence of fields from a fact to form a question and
#   an answer.
#
#   The q_fields and a_fields list contain tuples of the form:
#     (fact_key, required)
#
##############################################################################

class FactView(object):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, name):

        self.name = name

        self.active = True

        self.q_fields = []
        self.a_fields = []



    ##########################################################################
    #
    # question
    #
    ##########################################################################

    def question(self, fact):
        
        for field in self.q_fields:
            
            key = field[0]
            s = fact[key]

            for filter in get_fact_filters():
                s = filter.run(s)
                    
            q += "<div id=\"%s\">%s</div>" % key, fact[key]

        return q


            
    ##########################################################################
    #
    # answer
    #
    ##########################################################################

    def answer(self, fact):
        
        for field in self.a_fields:

            key = field[0]
            s = fact[key]

            for filter in get_fact_filters():
                s = filter.run(s)
                           
            a += "<div id=\"%s\">%s</div>" % key, fact[key]

        return a
            
        
