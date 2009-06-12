#
# both_ways.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter


class BothWays(CardType):

    id = "2"
    name = _("Front-to-back and back-to-front")

    # List and name the keys.
    fields = [("q", _("Question")),
              ("a", _("Answer"))]
    
    # Front-to-back.
    v1 = FactView("1", _("Front-to-back"))
    v1.q_fields = ["q"]
    v1.a_fields = ["a"]
    v1.required_fields = ["q"]

    # Back-to-front.
    v2 = FactView("2", _("Back-to-front"))
    v2.q_fields = ["a"]
    v2.a_fields = ["q"]
    v2.required_fields = ["q"]
    
    fact_views = [v1, v2]
    
    # The question field needs to be unique. As for duplicates in the answer
    # field, these are better handled through a synonym detection plugin.
    unique_fields = ["q"]


from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack

class FrontToBackToBothWays(CardTypeConverter):

    used_for = (FrontToBack, BothWays)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        # Update front-to-back view to corresponding view in new type.
        cards[0].fact_view = new_card_type.fact_views[0]
        
        # Create back-to-front view.
        new_card = Card(cards[0].fact, new_card_type.fact_views[1])
        new_cards, updated_cards, deleted_cards = [new_card], [cards[0]], []
        return new_cards, updated_cards, deleted_cards

 
class BothWaysToFrontToBack(CardTypeConverter):

    used_for = (BothWays, FrontToBack)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        new_cards, updated_cards, deleted_cards = [], [], []
        for card in cards:
            # Update front-to-back view to corresponding view in new type. 
            if card.fact_view == old_card_type.fact_views[0]:
                card.fact_view = new_card_type.fact_views[0]
                updated_cards = [card]
            # Delete back-to-front view.
            if card.fact_view == old_card_type.fact_views[1]:
                deleted_cards = [card]
        return new_cards, updated_cards, deleted_cards
