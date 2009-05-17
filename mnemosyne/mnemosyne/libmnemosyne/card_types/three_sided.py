#
# three_sided.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter


class ThreeSided(CardType):
    
    id = "3"
    name = _("Foreign word with pronunciation")

    # List and name the keys.
    fields = [("f", _("Foreign word")),
              ("p", _("Pronunciation")),
              ("t", _("Translation"))]

    # Recognition.
    v1 = FactView("1", _("Recognition"))
    v1.q_fields = ["f"]
    v1.a_fields = ["p", "t"]
    v1.required_fields = ["f"]

    # Production.
    v2 = FactView("2", _("Production"))
    v2.q_fields = ["t"]
    v2.a_fields = ["f", "p"]
    v2.required_fields = ["t"]
    
    fact_views = [v1, v2]

    # The foreign word field needs to be unique. As for duplicates in the
    # answer field, these are better handled through a synonym detection 
    # plugin.
    unique_fields = ["f"]


from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
from mnemosyne.libmnemosyne.card_types.both_ways import BothWays

class FrontToBackToThreeSided(CardTypeConverter):

    used_for = (FrontToBack, ThreeSided)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        # Update front-to-back view to corresponding view in new type.
        if "q" in correspondence and correspondence["q"] == "t":
            cards[0].fact_view = new_card_type.fact_views[1]
        else:
            cards[0].fact_view = new_card_type.fact_views[0]
        # Create back-to-front view.
        if "q" in correspondence and correspondence["q"] == "t":
            new_card = Card(cards[0].fact, new_card_type.fact_views[0])
        else:
            new_card = Card(cards[0].fact, new_card_type.fact_views[1])
        new_cards, updated_cards, deleted_cards = [new_card], [cards[0]], []
        return new_cards, updated_cards, deleted_cards


class BothWaysToThreeSided(CardTypeConverter):

    used_for = (BothWays, ThreeSided)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        for card in cards:
            if card.fact_view == old_card_type.fact_views[0]:
                if "q" in correspondence and correspondence["q"] == "t":
                    card.fact_view = new_card_type.fact_views[1]
                else:
                    card.fact_view = new_card_type.fact_views[0]
            elif card.fact_view == old_card_type.fact_views[1]:
                if "q" in correspondence and correspondence["q"] == "t":
                    card.fact_view = new_card_type.fact_views[0]
                else:
                    card.fact_view = new_card_type.fact_views[1]
        new_cards, updated_cards, deleted_cards = [], cards, []
        return new_cards, updated_cards, deleted_cards


class ThreeSidedToFrontToBack(CardTypeConverter):

    used_for = (ThreeSided, FrontToBack)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        new_cards, updated_cards, deleted_cards = [], [], []
        for card in cards:
            if card.fact_view == old_card_type.fact_views[0]:
                if "f" in correspondence and correspondence["f"] == "q":
                    card.fact_view = new_card_type.fact_views[0]
                    updated_cards.append(card)
                else:
                    deleted_cards.append(card)
            if card.fact_view == old_card_type.fact_views[1]:
                if "f" in correspondence and correspondence["f"] == "q":
                    deleted_cards.append(card)
                else:
                    card.fact_view = new_card_type.fact_views[0]
                    updated_cards.append(card)
        return new_cards, updated_cards, deleted_cards


class ThreeSidedToBothWays(CardTypeConverter):

    used_for = (ThreeSided, BothWays)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        for card in cards:
            if card.fact_view == old_card_type.fact_views[0]:
                if "f" in correspondence and correspondence["f"] == "q":
                    card.fact_view = new_card_type.fact_views[0]
                else:
                    card.fact_view = new_card_type.fact_views[1]                    
            if card.fact_view == old_card_type.fact_views[1]:
                if "f" in correspondence and correspondence["f"] == "q":
                    card.fact_view = new_card_type.fact_views[1]
                else:
                    card.fact_view = new_card_type.fact_views[0]
        new_cards, updated_cards, deleted_cards = [], cards, []
        return new_cards, updated_cards, deleted_cards
