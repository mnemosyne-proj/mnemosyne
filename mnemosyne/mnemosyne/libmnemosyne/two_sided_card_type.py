##############################################################################
#
# Two sided card type <Peter.Bienstman@UGent.be>
#
##############################################################################

from card_type import *



##############################################################################
#
# TwoSidedCardType
#
##############################################################################

class TwoSidedCardType(CardType):

    def new_cards(self, data):

        q, a, cat_name, id = data

        add_new_item(grade, q, a, cat_name, id)

    def update_cards(self, data):

        pass


register_card_type(TwoSidedCardType)
