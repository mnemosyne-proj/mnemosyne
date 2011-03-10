#
# card_type_converter.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class CardTypeConverter(Component):

    """Converts a set of sister cards to a new card type.

    used_for = (old_type class, new_type class)

    Note that the function of this class is NOT to edit the fact data behind
    the cards, which is trivial and handled in the main controller, but
    rather to delete, create or convert cards to make the transition to the
    new card type.

    'correspondence' {old_key: new_key} is the dictionary which relates fact
    keys in the two card types, in order to determine in which way cards
    should be created or deleted.

    We return 'new_cards', 'edited_cards', 'deleted_cards' in order to be able
    to handle them in the database storage.

    """

    component_type = "card_type_converter"

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        new_cards, edited_cards, deleted_cards = [], [], []
        return new_cards, edited_cards, deleted_cards
