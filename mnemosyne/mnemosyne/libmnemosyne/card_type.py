#
# card_type.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.component_manager import get_database


class CardType(Component):

    """A card type groups a number of fact views on a certain fact, thereby
    forming a set of related cards.

    A card type needs an id as well as a name, because the name can change
    for different translations. The description is used when card types are
    plugins, in order to give more information.

    The keys from the fact are also given more verbose names here.
    This is not done in fact.py, on one hand to save space in the database,
    and on the other hand to allow the possibilty that different card types
    give different names to the same key. (E.g. foreign word' could be
    called 'French' in a French card type, or'pronunciation' could be
    called 'reading' in a Kanji card type.) This in done in self.fields,
    which is a list of the form [(fact_key, fact_key_name)]. It is tempting to
    use a dictionary here, but we can't do that since ordering is important.

    We could use the component manager to track fact views, but this is
    probably overkill.

    """

    def __init__(self):
        self.id = "-1"
        self.name = ""
        self.description = ""
        self.fields = []
        self.fact_views = []
        self.unique_fields = []
        self.is_language = False
        self.widget = None
        self.css = ""
        self.a_on_top_of_q = False

    def required_fields(self):

        """Collect required fields from registered views."""

        s = set()
        for f in self.fact_views:
            for k in f.required_fields:
                s.add(k)
        return s

    def create_new_cards(self, fact_data, grade, cat_names):

        """Create a new set of related cards, using the kind of information
        that is easily obtainable through a GUI.

        """

        db = get_database()
        fact = Fact(fact_data, cat_names, self)
        db.add_fact(fact)
        for fact_view in self.fact_views:
            card = Card(grade, fact, fact_view)
            card.set_initial_grade(grade)
            db.add_card(card)

    def update_cards(self):
        raise NotImplementedError
