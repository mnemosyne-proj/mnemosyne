#
# sentence.py <Peter.Bienstman@UGent.be>
#

import re
import copy

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_types._cloze import get_q_a_from_cloze

cloze_re = re.compile(r"\[(.+?)\]", re.DOTALL)


class Sentence(CardType):

    """A card type using sentences to study foreign languages.

    Apart from simple recognition of the sentence, you can also add production
    cards using close deletion. E.g. if in the sentence field you write
    "La [casa:house] es [grande:big]", you'll get cards with questions like
    "La [house] es grande".

    """

    id = "6"
    name = _("Sentence")

    # List and name the keys.
    fact_keys_and_names = [("f", _("Sentence")),
                           ("p_1", _("Pronunciation")),
                           ("m_1", _("Meaning")),
                           ("n", _("Notes"))]

    # Recognition.
    v1 = FactView(_("Recognition"), "6.1")
    v1.q_fact_keys = ["f"]
    v1.a_fact_keys = ["p_1", "m_1", "n"]

    # Production.
    v2 = FactView(_("Production"), "6.2")
    v2.q_fact_keys = ["f"]  # Generated on the fly.
    v2.a_fact_keys = ["a", "p_1", "m_1", "n"] # Generated on the fly.

    fact_views = [v1, v2]
    unique_fact_keys = ["f"]
    required_fact_keys = ["f"]

    def fact_key_format_proxies(self):
        proxies = CardType.fact_key_format_proxies(self)
        proxies["a"] = "f"
        return proxies

    def fact_data(self, card):
        data = copy.copy(card.fact.data)
        # Recognition card.
        if card.fact_view == self.v1:
            question, answer = get_q_a_from_cloze\
                (card.fact["f"], -1)
        # Production card.
        else:
            question, answer = get_q_a_from_cloze\
                (card.fact["f"], card.extra_data["index"])
        data["f"] = question
        data["a"] = answer
        return data

    def create_sister_cards(self, fact):
        cards = [Card(self, fact, self.fact_views[0])]
        for match in cloze_re.finditer(fact["f"]):
            card = Card(self, fact, self.fact_views[1])
            card.extra_data["cloze"] = match.group(1)
            card.extra_data["index"] = len(cards) - 1
            cards.append(card)
        return cards

    def edit_sister_cards(self, fact, new_fact_data):
        # TODO
        new_cards, edited_cards, deleted_cards = [], [], []
        old_clozes = cloze_re.findall(fact["f"])
        new_clozes = cloze_re.findall(new_fact_data["f"])
        # If the number of clozes is equal, just edit the existing cards.
        if len(old_clozes) == len(new_clozes):
            for card in self.database().cards_from_fact(fact):
                index = card.extra_data["index"]
                card.extra_data["cloze"] = new_clozes[index]
                edited_cards.append(card)
        # If not, things are a little more complicated.
        else:
            new_clozes_processed = set()
            for card in self.database().cards_from_fact(fact):
                old_cloze  = card.extra_data["cloze"]
                index = card.extra_data["index"]
                if old_cloze in new_clozes:
                    new_index = new_clozes.index(old_cloze)
                    card.extra_data["cloze"] = new_clozes[new_index]
                    card.extra_data["index"] = new_index
                    new_clozes_processed.add(new_clozes[new_index])
                    edited_cards.append(card)
                else:
                    deleted_cards.append(card)
            for new_cloze in set(new_clozes).difference(new_clozes_processed):
                new_index = new_clozes.index(new_cloze)
                card = Card(self, fact, self.fact_views[0])
                card.extra_data["cloze"] = new_cloze
                card.extra_data["index"] = new_index
                new_cards.append(card)
        return new_cards, edited_cards, deleted_cards


class SentencePlugin(Plugin):

    name = _("Sentence")
    description = _("""A card type using sentences to study foreign languages.\n
Apart from simple recognition of the sentence, you can also add production cards using close deletion.\nE.g. if in the sentence field you write "La [casa:house] es [grande:big]", you'll get cards with questions like "La [house] es grande".""")
    components = [Sentence]
