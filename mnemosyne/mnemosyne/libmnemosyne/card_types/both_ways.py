#
# both_ways.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter


class BothWays(CardType):

    id = "2"
    name = _("Front-to-back and back-to-front")

    def __init__(self, language_name=""):
        CardType.__init__(self)
            
        # List and name the keys.
        self.fields.append(("q", _("Question")))
        self.fields.append(("a", _("Answer")))
        
        # Front-to-back.
        v = FactView(1, _("Front-to-back"))
        v.q_fields = ["q"]
        v.a_fields = ["a"]
        v.required_fields = ["q"]
        self.fact_views.append(v)
        
        # Back-to-front.
        v = FactView(2, _("Back-to-front"))
        v.q_fields = ["a"]
        v.a_fields = ["q"]
        v.required_fields = ["a"]
        self.fact_views.append(v)
        
        # The question field needs to be unique. As for duplicates is the answer
        # field, these are better handled through a synonym detection plugin.
        self.unique_fields = ["q"]


class FrontToBackToBothWays(CardTypeConverter):

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        # Update front-to-back view to corresponding view in new type.
        cards[0].fact_view = new_card_type.fact_views[0]
        
        # Create back-to-front view.
        new_card = Card(cards[0].fact, new_card_type.fact_views[1])
        new_cards, updated_cards, deleted_cards = [new_card], [cards[0]], []
        return new_cards, updated_cards, deleted_cards

 
class BothWaysToFrontToBack(CardTypeConverter):

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
        
