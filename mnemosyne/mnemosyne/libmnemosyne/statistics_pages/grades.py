#
# grades.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import numeric_string_cmp
from mnemosyne.libmnemosyne.statistics_page import StatisticsPage


class Grades(StatisticsPage):

    name = _("Grades")
    
    ALL_CARDS = -1

    def __init__(self, component_manager):
        StatisticsPage.__init__(self, component_manager)
        self.variants = [(self.ALL_CARDS, _("All cards"))]
        tags = []
        for cursor in self.database().con.execute(\
            "select _id, name from tags"):
            tags.append((cursor[0], cursor[1]))
        tags.sort(key=lambda x: x[1], cmp=numeric_string_cmp)
        for id, name in tags:
            self.variants.append((id, name))
        
    def prepare(self, variant):                
        self.plot_type = "histogram"
        self.title = _("Number of cards")
        self.xlabel = _("Grades")
        if variant == self.ALL_CARDS:
            self.data = [cursor[0] for cursor in self.database().con.execute(\
            "select grade from cards where active=1")]
        else:
            self.data = [cursor[0] for cursor in self.database().con.execute(\
            """select cards.grade from cards, tags_for_card where
            tags_for_card._card_id=cards._id and cards.active=1
            and tags_for_card._tag_id=?""", (variant,))]
        self.extra_hints['range'] = (0, 5)
        self.extra_hints['bins'] = 6

