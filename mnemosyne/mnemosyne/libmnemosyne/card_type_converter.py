#
# card_type_converter.py <Peter.Bienstman@UGent.be>
#


from mnemosyne.libmnemosyne.component import Component


class CardTypeConverter(Component):

    """Converts a set of related cards to a new card type.  Note that the
    function of this class is not to update the fact data behind the cards,
    which is trivial and handled in the main UI controller, but rather to
    delete, create or convert cards to make the transition to the new card
    type.

    """

    def convert(self, cards, new_card_type):
        pass
