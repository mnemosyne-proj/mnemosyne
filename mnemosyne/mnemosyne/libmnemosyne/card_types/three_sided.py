##############################################################################
#
# Three sided card type <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card import *
from mnemosyne.libmnemosyne.card_type import *
from mnemosyne.libmnemosyne.fact import *


##############################################################################
#
# ThreeSided
#
#  f: foreign word
#  p: pronunciation
#  t: translation
#
##############################################################################

class ThreeSided(CardType):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self):

        CardType.__init__(self, id=2,
                          name=_("Foreign word with pronunciation"),
                          can_be_unregistered=False)



    ##########################################################################
    #
    # generate_q
    #
    ##########################################################################

    def generate_q(self, fact, subtype):

        if subtype == 0:   # Recognition.
            return fact['f']
        elif subtype == 1: # Production.
            return fact['t'] 
        else:
            print 'Invalid subtype.'
            raise NameError()


        
    ##########################################################################
    #
    # generate_a
    #
    ##########################################################################

    def generate_a(self, fact, subtype):

        if subtype == 0:   # Recognition.
            return fact['p'] + '\n' + fact['t']
        elif subtype == 1: # Production.
            return fact['f'] + '\n' + fact['p']
        else:
            print 'Invalid subtype.'
            raise NameError()

        

    ##########################################################################
    #
    # new_cards
    #
    ##########################################################################

    def new_cards(self, data):

        # Extract and remove data.

        grade       = data['grade']
        cat_names   = data['cat_names']
        recognition = data['recognition']
        production  = data['production']
        
        del data['recognition']
        del data['production']
        del data['grade']

        # Create fact.

        # TODO: add subtypes as a category?

        fact = add_new_fact(data)

        if recognition:
            add_new_card(grade, card_type_id=self.id, fact=fact,
                                subcard=0, cat_names=cat_names)

        if production:
            add_new_card(grade, card_type_id=self.id, fact=fact,
                                subcard=1, cat_names=cat_names)
            
        self.widget.clear()



    ##########################################################################
    #
    # update_cards
    #
    ##########################################################################

    def update_cards(self, data):

        pass
