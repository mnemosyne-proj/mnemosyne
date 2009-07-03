#
# easiness.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import numeric_string_cmp
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage


class Easiness(PlotStatisticsPage):

    name = _("Easiness")
    
    ALL_CARDS = -1

    def __init__(self, component_manager):
        PlotStatisticsPage.__init__(self, component_manager)
        self.variants = [(self.ALL_CARDS, _("All cards"))]
        tags = []
        for cursor in self.database().con.execute(\
            "select _id, name from tags"):
            tags.append((cursor[0], cursor[1]))
        tags.sort(key=lambda x: x[1], cmp=numeric_string_cmp)
        for id, name in tags:
            self.variants.append((id, name))
        
    def prepare_statistics(self, variant):                
        if variant == self.ALL_CARDS:
            self.data = [cursor[0] for cursor in self.database().con.execute(\
            "select easiness from cards where active=1 and grade>=0")]
        else:
            self.data = [cursor[0] for cursor in self.database().con.execute(\
            """select cards.easiness from cards, tags_for_card where
            tags_for_card._card_id=cards._id and cards.active=1 and
            cards.grade>=0 and tags_for_card._tag_id=?""", (variant, ))]
