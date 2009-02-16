#
# three_sided.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter


class ThreeSided(CardType):
    
    id = "3"
    name = _("Foreign word with pronunciation")
            
    def __init__(self, language_name=""):
        CardType.__init__(self)

        # List and name the keys.
        self.fields.append(("f", _("Foreign word")))
        self.fields.append(("p", _("Pronunciation")))
        self.fields.append(("t", _("Translation")))

        # Recognition.
        v = FactView(1, _("Recognition"))
        v.q_fields = ["f"]
        v.a_fields = ["p", "t"]
        v.required_fields = ["f"]
        self.fact_views.append(v)

        # Production.
        v = FactView(2, _("Production"))
        v.q_fields = ["t"]
        v.a_fields = ["f", "p"]
        v.required_fields = ["t"]
        self.fact_views.append(v)
    
        # The foreign word field needs to be unique. As for duplicates is the
        # answer field, these are better handled through a synonym detection 
        # plugin.
        self.unique_fields = ["f"]


class FrontToBackToThreeSided(CardTypeConverter):

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
        new_card.set_initial_grade(0)
        new_cards, updated_cards, deleted_cards = [new_card], [cards[0]], []
        return new_cards, updated_cards, deleted_cards


class BothWaysToThreeSided(CardTypeConverter):

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
            else:
                raise ArgumentError
        new_cards, updated_cards, deleted_cards = [], cards, []
        return new_cards, updated_cards, deleted_cards


class ThreeSidedToFrontToBack(CardTypeConverter):

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
