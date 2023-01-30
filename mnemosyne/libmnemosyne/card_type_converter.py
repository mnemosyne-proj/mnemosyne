#
# card_type_converter.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component


class CardTypeConverter(Component):

    """Converts a set of sister cards to a new card type.

    used_for = CardTypeConverter.card_type_converter_key\
        (old_type class, new_type class)

    Note that the function of this class is NOT to edit the fact data behind
    the cards, which is trivial and handled in the main controller, but
    rather to delete, create or convert cards to make the transition to the
    new card type.

    'correspondence' {old_fact_key: new_fact_key} is the dictionary which
    relates fact keys in the two card types, in order to determine in which
    way cards should be created or deleted.

    We return 'new_cards', 'edited_cards', 'deleted_cards' in order to be able
    to handle them in the database storage.

    """

    component_type = "card_type_converter"


    def card_type_converter_key(old_card_type, new_card_type):

        """Creates a single key to store a card type converter in the
        component_manager.

        """

        # Convenience to allow to work with both classes and instances.
        if type(old_card_type) == type:
            return old_card_type.__name__ + "__TO__" + \
                new_card_type.__name__
        else:
            return old_card_type.__class__.__name__ + "__TO__" + \
                new_card_type.__class__.__name__

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        new_cards, edited_cards, deleted_cards = [], [], []
        return new_cards, edited_cards, deleted_cards
