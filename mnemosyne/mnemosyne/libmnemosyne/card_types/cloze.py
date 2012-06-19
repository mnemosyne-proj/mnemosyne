#
# cloze.py <Peter.Bienstman@UGent.be>
#

import re

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.card_types._cloze import get_q_a_from_cloze

cloze_re = re.compile(r"\[(.+?)\]", re.DOTALL)


class Cloze(CardType):

    """CardType to do cloze deletion on a string, e.g. "The political parties in
    the US are the [democrats] and the [republicans]." would give the following
    cards:

    Q:The political parties in the US are the [...] and the republicans.
    A:democrats

    Q:The political parties in the US are the democrats and the [...].
    A:republicans

    Illustration of a CardType which does not use the traditional FactView
    mechanism.

    This is implemented by creating cards which contain extra_data entries
    "cloze" and "index", containing e.g. "democrats" and 0. Storing both the
    cloze and its index allows us to have enough data to support all possible
    editing operations.

    """

    id = "5"
    name = _("Cloze deletion")

    fact_keys_and_names = [("text", _("Text"))]
    unique_fact_keys = ["text"]

    v = FactView(_("Cloze"), "5.1")
    v.q_fact_keys = ["f"]  # Generated on the fly.
    v.a_fact_keys = ["b"]  # Generated on the fly.
    fact_views = [v]

    def fact_key_format_proxies(self):
        return {"text": "text", "f": "text", "b": "text"}

    def is_fact_data_valid(self, fact_data):
        return bool(cloze_re.search(fact_data["text"]))

    def fact_data(self, card):
        question, answer = get_q_a_from_cloze\
            (card.fact["text"], card.extra_data["index"])
        return {"f": question, "b": answer}

    def create_sister_cards(self, fact):
        cards = []
        for match in cloze_re.finditer(fact["text"]):
            card = Card(self, fact, self.fact_views[0])
            card.extra_data["cloze"] = match.group(1)
            card.extra_data["index"] = len(cards)
            cards.append(card)
        return cards

    def edit_sister_cards(self, fact, new_fact_data):
        new_cards, edited_cards, deleted_cards = [], [], []
        if "text" in fact.data.keys():
            old_clozes = cloze_re.findall(fact["text"])
        else:  # Coming from card type conversion.
            old_clozes = []
        new_clozes = cloze_re.findall(new_fact_data["text"])
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


class ClozePlugin(Plugin):

    name = _("Cloze deletion")
    description = _("""A card type blanking out certain fragments in a text.\n
E.g., the text \"The capital of [France] is [Paris]\", will give cards with questions \"The capital of France is [...].\" and \"The capital of [...] is Paris\".\n
Editing the text will automatically update all sister cards.\n\nYou can also specify hints, e.g. [cloze:hint] will show
 [hint] in the question as opposed to [...].""")
    components = [Cloze]
