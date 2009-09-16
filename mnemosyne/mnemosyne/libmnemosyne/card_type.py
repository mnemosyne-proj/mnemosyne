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
    
    The keys from the fact are also given more verbose names here.
    This is not done in fact.py, on one hand to save space in the database,
    and on the other hand to allow the possibility that different card types
    give different names to the same key. (E.g. foreign word' could be
    called 'French' in a French card type, or 'pronunciation' could be
    called 'reading' in a Kanji card type.) This in done in self.fields,
    which is a list of the form [(fact_key, fact_key_name)]. It is tempting to
    use a dictionary here, but we can't do that since ordering is important.

    Fields which need to be different for all facts belonging to this card
    type are listed in unique_fields.

    Note that a fact could contain more data than those listed in the card
    type's 'fields' variable, which could be useful for card types needing
    hidden fields.

    We could use the component manager to track fact views, but this is
    probably overkill.
    
    The renderer is determined only when we need it, as opposed to when we
    create the card type, because it is not sure that the renderer already
    exists at that stage.

    The functions create_related_cards and update_related_cards and
    after_review provide an extra layer of abstraction and can be overridden
    by card types like cloze deletion, which require a varying number of fact
    views with card specific data.

    """

    # Id is a class variable to allow extra way of determining inheritance
    # hierarchy.

    id = "-1"
    name = ""
    component_type = "card_type"
    renderer = None

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

    def is_data_valid(self, fact_data):
        for required in self.required_fields:
            if not fact_data[required]:
                return False
        return True
        
    def question(self, card):
        return self.get_renderer().render_card_fields(card.fact,
                                                      card.fact_view.q_fields)

    def answer(self, card):
        return self.get_renderer().render_card_fields(card.fact,
                                                      card.fact_view.a_fields)
        
    def get_renderer(self):
        if self.renderer:
            return self.renderer
        else:
            self.renderer = self.component_manager.\
                   get_current("renderer", used_for=self.__class__)
            if not self.renderer:
                 self.renderer = self.component_manager.get_current("renderer")
            return self.renderer

    # The following functions allow for the fact that all the logic
    # corresponding to specialty card types (like cloze deletion) can be
    # contained in a single derived class by reimplementing these functions.
    # These functions should only deal with creating, deleting, ... Card
    # objects. Initial grading and storing in the database is done in the
    # main controller.

    def create_related_cards(self, fact):
        return [Card(fact, fact_view) for fact_view in self.fact_views]

    def update_related_cards(self, fact, new_fact_data):

        """If for the card type this operation results in updated, added or
        deleted card data apart from the updated fact data from which they
        derive, these should be returned here, so that they can be taken into
        account in the database storage.

        """

        new_cards, updated_cards, deleted_cards = [], [], []
        return new_cards, updated_cards, deleted_cards
    
    def before_repetition(self, card):
        return

    def after_repetition(self, card):
        return
