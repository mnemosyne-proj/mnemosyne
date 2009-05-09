#
# card_type.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.component_manager import card_types
from mnemosyne.libmnemosyne.component_manager import component_manager


class CardType(Component):

    """A card type groups a number of fact views on a certain fact, thereby
    forming a set of related cards.

    A card type needs an id as well as a name, because the name can change
    for different translations. The description is used when card types are
    plugins, in order to give more information.

    Inherited card types should have ids where dots separate the different
    levels of the hierarchy, e.g. parent_id.child_id. For card types which
    don't have code of their own, but are only a clone of an existing card
    type, the parent id should be followed by _CLONED, e.g.
    3_CLONED.Japanese

    The keys from the fact are also given more verbose names here.
    This is not done in fact.py, on one hand to save space in the database,
    and on the other hand to allow the possibility that different card types
    give different names to the same key. (E.g. foreign word' could be
    called 'French' in a French card type, or 'pronunciation' could be
    called 'reading' in a Kanji card type.) This in done in self.fields,
    which is a list of the form [(fact_key, fact_key_name)]. It is tempting to
    use a dictionary here, but we can't do that since ordering is important.

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
    is_clone = False
    component_type = "card_type"
    
    def __init__(self):
        self.fields = []
        self.fact_views = []
        self.unique_fields = []
        self.widget = None
        self.renderer = None
        
    def __eq__(self, other):
        try:
            return self.id == other.id
        except:
            return False
        
    def keys(self):
        return set(fact_key for (fact_key, fact_key_name) in self.fields)

    def key_names(self):
        return [fact_key_name for (fact_key, fact_key_name) in self.fields]
    
    def key_with_name(self, key_name):
        for fact_key, fact_key_name in self.fields:
            if fact_key_name == key_name:
                return fact_key

    def required_fields(self):

        """Collect required fields from registered views."""

        s = set()
        for f in self.fact_views:
            for k in f.required_fields:
                s.add(k)
        return s

    def validate_data(self, fact_data):

        """If a card type needs to validate its data apart from asking that
        all the required fields are there, this can be done here.

        """
        
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
            self.renderer = component_manager.\
                   get_current("renderer", used_for=self.__class__)
            if not self.renderer:
                 self.renderer = component_manager.get_current("renderer")
            return self.renderer

    def clone(self, clone_name):
        clone_id = self.id + "_CLONED." + clone_name
        if clone_id in [card_type.id for card_type in card_types()]:
            raise NameError
        # Create a safe version of the name to be used as class name.
        # TODO: not fool proof yet, but captures the most obvious cases.   
        clone_name_safe = clone_name.encode('utf8').replace(" ", "_")  
        C = type(clone_name_safe, (self.__class__, ),
                 {"name": clone_name,
                  "is_clone": True,
                  "id": clone_id})
        component_manager.register(C())

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

    def after_review(self, card):
        return
