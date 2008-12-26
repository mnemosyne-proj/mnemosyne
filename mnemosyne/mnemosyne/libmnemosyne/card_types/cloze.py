#
# cloze.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.fact_view import FactView


class Cloze(CardType, Plugin):
    
    """CardType to do cloze deletion on a string, e.g. "The political parties in
    the US are the [democrats] and the [republicans]." would give the following
    cards:
    
    Q:The political parties in the US are the [...] and the [republicans].
    A:democrats
    
    Q:The political parties in the US are the democrats and the [...].
    A:republicans
    
    Not yet fully implemented, its main purpose is to provide a skeleton of a 
    CardType which does not use the traditional FactView mechanism.
    
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
        self.fact_views_can_be_deactivated = False
        
    # Perhaps it's a good idea to store into each FactView.extra_data both the 
    # word to be deleted and its position. E.g., the first cloze FactView stores
    # ("democrats", 0) and the second one ("republicans", 2).
    # The difficulty in implementing this card type is to make sure that when
    # editing the string (adding clozes, removing clozes, editing clozes),
    # text to be deleted), all the data stays consistent, and storing all that
    # information could help making that possible.
        
    def question(self, fact, fact_view)
        return fact.text.replace(fact_view.extra_data[0], "[...]",  1)

    def answer(self, fact, fact_view):
        return fact_view.extra_data[0]
 
    def create_related_cards(self, fact, grade=0):
        raise NotImplementedError
        #cards = []
        #for each cloze:
        #    create fact view for cloze
        #    db.add_fact_view(fact_view)
        #    card = Card(fact, fact_view)
        #    card.set_initial_grade(grade)
        #    card.append(card)
        #    return card

    def update_related_cards(self, fact, new_fact_data):
        raise NotImplementedError
        # This is the hard part to implement, as updating the data can
        # result in the creation and deletion of new clozes, which then
        # have to get a new fact view, all at the same time making sure
        # that the previously created cards still correspond to their
        # earlier cloze.

