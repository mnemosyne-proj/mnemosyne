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
#   give different names to the same key. (E.g. foreign word' could be
#   called 'French' in a French card type, or'pronunciation' could be
#   called 'reading' in a Kanji card type.)
#
#   We could use the component manager to track fact views, but this is
#   probably overkill.
#
##############################################################################

class CardType(Component):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self):
        
        self.id               = -1
        self.name             = ""
        self.description      = ""
        
        self.fact_views       = []         
        self.fact_key_names   = {}
        self.unique_fact_keys = "" # For duplicate checking.

        self.is_language      = False

        self.widget           = None
        self.css              = ""
        self.a_on_top_of_q    = False
        self.is_language      = False



    ##########################################################################
    #
    # new_cards
    #
    ########################################################################## 

    def new_cards(self, fact_data, grade, cat_names):

        db = get_database()

        # Create fact.

        fact = Fact(fact_data)
        db.save_fact(fact)

        # Create cards.

        for fact_view in self.fact_views:

            card = Card(grade=grade, card_type=self, fact=fact,
                        fact_view=fact_view, cat_names=cat_names)
        
            db.save_card(card)


            
    ##########################################################################
    #
    # update_cards
    #
    ##########################################################################
    
    def update_cards(self):
        raise NotImplementedError
