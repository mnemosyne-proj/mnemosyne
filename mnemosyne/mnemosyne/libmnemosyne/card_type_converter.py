
#
# card_type_converter.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class CardTypeConverter(Component):

    """Converts a set of related cards to a new card type.

    "used_for" should be set to the tuple (old_type class, new_type class)

    Note that the function of this class is not to edit the fact data behind
    the cards, which is trivial and handled in the main UI controller, but
    rather to delete, create or convert cards to make the transition to the
    new card type.

    'correspondence' is the dictionary which relates fact keys in the two
    card types, in order to determine in which way cards should be created
    or deleted.

    The returned values are to be able to edit the results in the database.

    """

    component_type = "card_type_converter"

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        new_cards, edited_cards, deleted_cards = [], [], []
        return new_cards, edited_cards, deleted_cards