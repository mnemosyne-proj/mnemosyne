#
# card_type.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import component_manager

class CardType(object):

    """A card type groups a number of fact views on a certain fact, thereby
    forming a set of related cards.

    A card type needs an id as well as a name, because the name can change
    for different translations. The description is used when card types are
    plugins, in order to give more information.

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
    can_be_subclassed = True
    defined_through_gui = False

    def __init__(self):
        self.fields = []
        self.fact_views = []
        self.unique_fields = []
        self.widget = None
        self.renderer = None
        self.fact_views_can_be_deactivated = True

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
        
    def question(self, fact, fact_view):
        return self.get_renderer().render_card_fields(fact, fact_view.q_fields)

    def answer(self, fact, fact_view):
        return self.get_renderer().render_card_fields(fact, fact_view.a_fields)
        
    def get_renderer(self):
        if self.renderer:
            return self.renderer
        else:
            self.renderer = component_manager.\
                   get_current("renderer", used_for=self.__class__)
            if not self.renderer:
                 self.renderer = component_manager.get_current("renderer")
            return self.renderer

    # The following functions allow for the fact that all the logic
    # corresponding to specialty card types (like cloze deletion) can be
    # contained in a single derived class by reimplementing these functions.

    def create_related_cards(self, fact, grade=0):
        cards = []
        for fact_view in self.fact_views:
            card = Card(fact, fact_view)
            card.set_initial_grade(grade)
            cards.append(card)
        return cards

    def update_related_cards(self, fact, new_fact_data):

        """If for the card type this operation results in updated or added
        card data apart from the updated fact data from which they derive,
        these should be returned here, so that they can be taken into account
        in the database storage.

        """
        
        fact.data = new_fact_data
        new_cards, updated_cards = [], []
        return new_cards, updated_cards

    def after_review(self, card):
        return
