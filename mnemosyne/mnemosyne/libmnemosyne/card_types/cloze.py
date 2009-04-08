#
# cloze.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

import re

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.component_manager import database

cloze_re = re.compile(r"\[(.+?)\]", re.DOTALL)

manual = _("This card type can be used to blank fragments in a text, e.g.")
manual += " \n" + _("\"The capital of France is [Paris]\",")
manual += " " + _("will give a card with question") + "\n"
manual += _("\"The capital of France is [...]\"")


class Cloze(CardType, Plugin):
    
    """CardType to do cloze deletion on a string, e.g. "The political parties in
    the US are the [democrats] and the [republicans]." would give the following
    cards:
    
    Q:The political parties in the US are the [...] and the republicans.
    A:democrats
    
    Q:The political parties in the US are the democrats and the [...].
    A:republicans
    
    Illustration of a CardType which does not use the traditional FactView
    mechanism.

    This is implemented by creating cards which contain extra_data fields
    ("democrats", 0) and ("republicans", 1) respectively (or more precisely,
    their representation as a string, as that is the type that is stored in
    the database.
    
    """
    
    provides = "card_type"

    def __init__(self):
        CardType.__init__(self)
        self.id = "5"
        self.name = _("Cloze deletion")
        self.description = \
           _("A card type blanking out certain fragments in a text.")
        self.fields.append(("text", _("Text")))
        self.unique_fields = ["text"]
        self.fact_views = [FactView(1, _("Cloze"))]
        self.activation_message = manual

    def validate_data(self, fact_data):
        return "[" in fact_data["text"] and "]" in fact_data["text"]
        
    def question(self, card):
        extra_data = eval(card.extra_data)
        question = card.fact["text"].replace("[", "").replace("]", "")
        question = question.replace(extra_data[0], "[...]",  1)
        return self.get_renderer().render_text(question, "text",
                                               card.fact.card_type)

    def answer(self, card):
        answer = eval(card.extra_data)[0]
        return self.get_renderer().render_text(answer, "text",
                                               card.fact.card_type)

    def create_related_cards(self, fact, grade=0):
        cards = []
        for match in cloze_re.finditer(fact["text"]):
            card = Card(fact, self.fact_views[0])
            card.set_initial_grade(grade)
            card.extra_data = repr((match.group(1), len(cards)))
            card.id += "." + str(len(cards)) # Make id unique.
            cards.append(card)         
        return cards

    def update_related_cards(self, fact, new_fact_data):

        """Now learning data is only preserved in case the number of clozes
        stays the same. This could in theory be made more sophisticated, but it's
        probably a corner case anyhow.

        """
        
        new_cards, updated_cards, deleted_cards = [], [], []
        if new_fact_data["text"].count("[") == fact["text"].count("["):
            new_clozes = []
            for match in cloze_re.finditer(new_fact_data["text"]):
                new_clozes.append(match.group(1))
            for card in database().cards_from_fact(fact):
                index = eval(card.extra_data)[1]
                card.extra_data = repr((new_clozes[index], index))
                updated_cards.append(card)
        else:
            for card in database().cards_from_fact(fact):
                database().delete_card(card)
            fact.data = new_fact_data
            new_cards = self.create_related_cards(fact)
        return new_cards, updated_cards, deleted_cards


