#
# card_type.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.utils import CompareOnId
from mnemosyne.libmnemosyne.component import Component


class CardType(Component, CompareOnId):

    """A card type groups a number of fact views on a certain fact, thereby
    forming a set of sister cards.

    A card type needs an id as well as a name, because the name can change
    for different translations. Built-in card types will have an id which
    maps to an integer, user card types should not have this property.

    Inherited card types should have ids where :: separates the different
    levels of the hierarchy, e.g. parent_id::child_id.
    
    The keys from the fact are also given more verbose names here. This is
    not done in fact.py, on one hand to save space in the database, and on
    the other hand to allow the possibility that different card types give
    different names to the same key. (E.g. foreign word' could be called
    'French' in a French card type, or 'pronunciation' could be called
    'reading' in a Kanji card type.) This is done in self.fields, which is
    a list of the form [(fact_key, fact_key_name)]. It is tempting to use a
    dictionary here, but we can't do that since ordering is important.

    Fields which need to be different for all facts belonging to this card
    type are listed in 'unique_fields'.

    Note that a fact could contain more data than those listed in the card
    type's 'fields' variable, which could be useful for card types needing
    hidden fields, dynamically generated fields, ... .

    We could use the component manager to track fact views, but this is
    probably overkill.

    The functions 'create_sister_cards' and 'edit_sister_cards' can be
    overridden by card types which can have a varying number of fact views,
    e.g. the cloze card type.

    """
    
    id = "-1"
    name = ""
    component_type = "card_type"

    fields = None
    fact_views = None
    unique_fields = None
    required_fields = None
    keyboard_shortcuts = {}
    extra_data = {}

    def keys(self):
        return set(fact_key for (fact_key, fact_key_name) in self.fields)

    def key_names(self):
        return [fact_key_name for (fact_key, fact_key_name) in self.fields]
    
    def key_with_name(self, key_name):
        for fact_key, fact_key_name in self.fields:
            if fact_key_name == key_name:
                return fact_key
            
    def render_question(self, card, render_chain="default", **render_args):
        return self.render_chain(render_chain).\
            render_question(card, **render_args)
       
    def render_answer(self, card, render_chain="default", **render_args):
        return self.render_chain(render_chain).\
            render_answer(card, **render_args)

    def is_data_valid(self, fact_data):

        """Check if all the required fields are present."""
        
        for required in self.required_fields:
            if required not in fact_data or not fact_data[required]:
                return False
        return True
        
    def fact_data(self, card):

        """Returns the data in fact of a card. Normally. this is just
        'card.fact.data', but specialty card types (e.g. the cloze card type)
        can override this.

        """
        
        return card.fact.data

    def create_sister_cards(self, fact):

        """Initial grading of cards and storing in the database should not happen
        here, but is done in the main controller.

        """
        
        return [Card(self, fact, fact_view) for fact_view in self.fact_views]

    def edit_sister_cards(self, fact, new_fact_data):

        """If for the card type this operation results in edited, added or
        deleted card data apart from the edited fact data from which they
        derive, these should be returned here, so that they can be taken into
        account in the database storage.

        Initial grading of cards and storing in the database should not happen
        here, but is done in the main controller.

        """

        new_cards, edited_cards, deleted_cards = [], [], []
        return new_cards, edited_cards, deleted_cards
    
    def key_format_proxies(self):

        """Sometimes, a card type can dynamically create a field when
        generating a question or an answer (see e.g. the cloze card type).
        Since the user cannot specify how this key should be formatted, it
        should be formatted like an other, static key. This function returns
        a dictionary with this correspondence.

        """

        proxies = {}
        for fact_key, fact_key_name in self.fields:
            proxies[fact_key] = fact_key
        return proxies
