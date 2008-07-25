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
from mnemosyne.libmnemosyne.config import config



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

    recognition = 0
    production = 1

    def __init__(self):

        CardType.__init__(self, id=2,
                          name=_("Foreign word with pronunciation"),
                          can_be_unregistered=False)



    ##########################################################################
    #
    # generate_q
    #
    ##########################################################################

    def generate_q(self, fact, fact_view):

        if fact_view == ThreeSided.recognition:
            return fact['f']
        elif fact_view == ThreeSided.production:
            return fact['t'] 
        else:
            print 'Invalid fact view.'
            raise NameError()


        
    ##########################################################################
    #
    # generate_a
    #
    ##########################################################################

    def generate_a(self, fact, fact_view):

        if fact_view == ThreeSided.recognition:
            return fact['p'] + '\n' + fact['t']
        elif fact_view == ThreeSided.production:
            return fact['f'] + '\n' + fact['p']
        else:
            print 'Invalid fact view.'
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

        # TODO: add fact_views as a category name

        fact = Fact(data)
        fact.save()

        if recognition:
            
            Card(grade, card_type=self, fact=fact,
                 fact_view=ThreeSided.recognition, cat_names=cat_names).save()

        if production:
            Card(grade, card_type=self, fact=fact,
                 fact_view=ThreeSided.production, cat_names=cat_names).save()
            
        self.widget.clear()



    ##########################################################################
    #
    # update_cards
    #
    ##########################################################################

    def update_cards(self, data):

        pass
