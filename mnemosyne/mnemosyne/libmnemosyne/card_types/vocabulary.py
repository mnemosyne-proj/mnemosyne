#
# vocabulary.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter


class Vocabulary(CardType):
    
    id = "3"
    name = _("Vocabulary")

    # List and name the keys.
    fields = [("f", _("Foreign word or expression")),
              ("p_1", _("Pronunciation")),
              ("m_1", _("Meaning")),
              ("n", _("Notes"))]

    # Recognition.
    v1 = FactView(_("Recognition"), "3.1")
    v1.q_fields = ["f"]
    v1.a_fields = ["p_1", "m_1", "n"]

    # Production.
    v2 = FactView(_("Production"), "3.2")
    v2.q_fields = ["m_1"]
    v2.a_fields = ["f", "p_1", "n"]
    
    fact_views = [v1, v2]
    unique_fields = ["f"]
    required_fields = ["f", "m_1"]

from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
from mnemosyne.libmnemosyne.card_types.both_ways import BothWays

class FrontToBackToVocabulary(CardTypeConverter):

    used_for = (FrontToBack, Vocabulary)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        # Update front-to-back view to corresponding view in new type.
        if "f" in correspondence and correspondence["f"] == "m_1":
            cards[0].fact_view = new_card_type.fact_views[1]
        else:
            cards[0].fact_view = new_card_type.fact_views[0]
        # Create back-to-front view.        
        if "f" in correspondence and correspondence["f"] == "m_1":
            new_card = Card(new_card_type, cards[0].fact,
                new_card_type.fact_views[0])
        else:
            new_card = Card(new_card_type, cards[0].fact,
                new_card_type.fact_views[1])
        new_cards, edited_cards, deleted_cards = [new_card], [cards[0]], []
        return new_cards, edited_cards, deleted_cards


class BothWaysToVocabulary(CardTypeConverter):

    used_for = (BothWays, Vocabulary)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        for card in cards:
            if card.fact_view == old_card_type.fact_views[0]:
                if "f" in correspondence and correspondence["f"] == "m_1":
                    card.fact_view = new_card_type.fact_views[1]
                else:
                    card.fact_view = new_card_type.fact_views[0]
            if card.fact_view == old_card_type.fact_views[1]:
                if "f" in correspondence and correspondence["f"] == "m_1":
                    card.fact_view = new_card_type.fact_views[0]
                else:
                    card.fact_view = new_card_type.fact_views[1]
        new_cards, edited_cards, deleted_cards = [], cards, []
        return new_cards, edited_cards, deleted_cards


class VocabularyToFrontToBack(CardTypeConverter):

    used_for = (Vocabulary, FrontToBack)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        new_cards, edited_cards, deleted_cards = [], [], []
        for card in cards:
            if card.fact_view == old_card_type.fact_views[0]:
                if "f" in correspondence and correspondence["f"] == "f":
                    card.fact_view = new_card_type.fact_views[0]
                    edited_cards.append(card)
                else:
                    deleted_cards.append(card)
            if card.fact_view == old_card_type.fact_views[1]:
                if "f" in correspondence and correspondence["f"] == "f":
                    deleted_cards.append(card)
                else:
                    card.fact_view = new_card_type.fact_views[0]
                    edited_cards.append(card)
        return new_cards, edited_cards, deleted_cards


class VocabularyToBothWays(CardTypeConverter):

    used_for = (Vocabulary, BothWays)

    def convert(self, cards, old_card_type, new_card_type, correspondence):
        for card in cards:
            if card.fact_view == old_card_type.fact_views[0]:
                if "f" in correspondence and correspondence["f"] == "f":
                    card.fact_view = new_card_type.fact_views[0]
                else:
                    card.fact_view = new_card_type.fact_views[1]                    
            if card.fact_view == old_card_type.fact_views[1]:
                if "f" in correspondence and correspondence["f"] == "f":
                    card.fact_view = new_card_type.fact_views[1]
                else:
                    card.fact_view = new_card_type.fact_views[0]
        new_cards, edited_cards, deleted_cards = [], cards, []
        return new_cards, edited_cards, deleted_cards
