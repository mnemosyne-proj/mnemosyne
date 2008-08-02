##############################################################################
#
# card_type.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from mnemosyne.libmnemosyne.component import Component

# TODO: document


##############################################################################
#
# CardType
#
#   The keys from the fact are also given more verbose names here. This is
#   not done in fact.py, on one hand to save space in the database, and
#   on the other hand to allow the possibilty that different card types
#   give different names to the same key. (E.g. 'pronunciation' could be
#   called 'reading' in a Kanji card type).
#
##############################################################################

class CardType(Component):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, id, name, description=""):

        self.fact_views = []

        self.fact_key_names = {}
        
        self.id                  = id
        self.name                = name
        self.description         = description
        #self.widget_class        = None
        #self.widget              = None
        self.css                 = ""
        self.a_on_top_of_q       = False



    ##########################################################################
    #
    # Functions to be implemented by the specific card types.
    #
    ########################################################################## 

    def new_cards(self):
        raise NotImplementedError

    def update_cards(self):
        raise NotImplementedError
