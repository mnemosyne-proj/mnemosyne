#
# both_ways.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter


class BothWays(CardType):

    id = "2"
    name = _("Front-to-back and back-to-front")

    # List and name the keys.
    fact_keys_and_names = [("f", _("Front")),
                           ("b", _("Back"))]

    # Front-to-back.
    v1 = FactView(_("Front-to-back"), "2.1")
    v1.q_fact_keys = ["f"]
    v1.a_fact_keys = ["b"]

    # Back-to-front.
    v2 = FactView(_("Back-to-front"), "2.2",)
    v2.q_fact_keys = ["b"]
    v2.a_fact_keys = ["f"]

    fact_views = [v1, v2]
    required_fact_keys = ["f", "b"]
    unique_fact_keys = ["f"]


from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack

class FrontToBackToBothWays(CardTypeConverter):

    used_for = CardTypeConverter.card_type_converter_key\
        (FrontToBack, BothWays)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        # Update front-to-back view to corresponding view in new type.
        cards[0].fact_view = new_card_type.fact_views[0]
        # Create back-to-front view.
        new_card = Card(new_card_type, cards[0].fact,
            new_card_type.fact_views[1])
        new_cards, edited_cards, deleted_cards = [new_card], [cards[0]], []
        return new_cards, edited_cards, deleted_cards


class BothWaysToFrontToBack(CardTypeConverter):

    used_for = CardTypeConverter.card_type_converter_key\
        (BothWays, FrontToBack)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        new_cards, edited_cards, deleted_cards = [], [], []
        for card in cards:
            # Update front-to-back view to corresponding view in new type.
            if card.fact_view == old_card_type.fact_views[0]:
                card.fact_view = new_card_type.fact_views[0]
                edited_cards = [card]
            # Delete back-to-front view.
            elif card.fact_view == old_card_type.fact_views[1]:
                deleted_cards = [card]
            else:
                raise ArgumentError("Invalid fact view.")
        return new_cards, edited_cards, deleted_cards
