#
# card_type.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.utils import CompareOnId
from mnemosyne.libmnemosyne.component import Component


class CardType(Component, CompareOnId):

    """A card type groups a number of fact views on a certain fact, thereby
    forming a set of related cards.

    A card type needs an id as well as a name, because the name can change
    for different translations.

    Inherited card types should have ids where :: separates the different
    levels of the hierarchy, e.g. parent_id::child_id.
    
    The keys from the fact are also given more verbose names here, as well
    as an optional language code, e.g. for text-to-speech processing.
    This is not done in fact.py, on one hand to save space in the database,
    and on the other hand to allow the possibility that different card types
    give different names to the same key. (E.g. foreign word' could be
    called 'French' in a French card type, or 'pronunciation' could be
    called 'reading' in a Kanji card type.) This in done in self.fields,
    which is a list of the form [(fact_key, fact_key_name, language_code)].
    It is tempting to use a dictionary here, but we can't do that since
    ordering is important.

    Fields which need to be different for all facts belonging to this card
    type are listed in unique_fields.

    Note that a fact could contain more data than those listed in the card
    type's 'fields' variable, which could be useful for card types needing
    hidden fields.

    We could use the component manager to track fact views, but this is
    probably overkill.
    
    The functions create_related_cards and edit_related_cards and
    after_review provide an extra layer of abstraction and can be overridden
    by card types like cloze deletion, which require a varying number of fact
    views with card specific data.

    """
    
    id = "-1"
    name = ""
    component_type = "card_type"
    _renderer = None

    fields = None
    fact_views = None
    unique_fields = None
    required_fields = None
    keyboard_shortcuts = {}
    extra_data = {}

    def keys(self):
        return set(fact_key for (fact_key, fact_key_name,
                   fact_key_language) in self.fields)

    def key_names(self):
        return [fact_key_name for (fact_key, fact_key_name,
               fact_key_language) in self.fields]
    
    def key_with_name(self, key_name):
        for fact_key, fact_key_name, fact_key_language in self.fields:
            if fact_key_name == key_name:
                return fact_key

    def is_data_valid(self, fact_data):
        for required in self.required_fields:
            if not fact_data[required]:
                return False
        return True

    # All the following functions allow for the fact that all the logic
    # corresponding to specialty card types (like cloze deletion) can be
    # contained in a single derived class by reimplementing these functions.
    # The default implementation provided here is for fact-based cards.
        
    def question(self, card, render_chain="default", **render_args):        
        return self.renderer(render_chain).render_fields(card.fact,
            card.fact_view.q_fields, self, render_chain, **render_args)

    def answer(self, card, render_chain="default", **render_args):
        return self.renderer(render_chain).render_fields(card.fact,
            card.fact_view.a_fields, self, render_chain, **render_args)
    
    # The following functions should only deal with creating, deleting, ...
    # Card objects. Initial grading and storing in the database is done in
    # the main controller.

    def create_related_cards(self, fact):
        return [Card(fact, fact_view) for fact_view in self.fact_views]

    def edit_related_cards(self, fact, new_fact_data):

        """If for the card type this operation results in edited, added or
        deleted card data apart from the edited fact data from which they
        derive, these should be returned here, so that they can be taken into
        account in the database storage.

        """

        new_cards, edited_cards, deleted_cards = [], [], []
        return new_cards, edited_cards, deleted_cards
    
    def before_repetition(self, card):
        return

    def after_repetition(self, card):
        return
