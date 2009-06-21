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
        self.plot_type = "barchart"
        self.title = _("Number of cards")
        self.xlabel = _("Grades")
        self.data = []
        if variant == self.ALL_CARDS:
            for grade in range (-1,6):
                self.data.append(self.database().con.execute(\
                    "select count() from cards where grade=? and active=1",
                     (grade, )).fetchone()[0])   
        else:
            for grade in range (-1,6):
                self.data.append(self.database().con.execute(\
                    """select count() from cards, tags_for_card where
                    tags_for_card._card_id=cards._id and cards.active=1
                    and tags_for_card._tag_id=? and grade=?""",
                    (variant, grade)).fetchone()[0])
        self.xvalues = range(-1, 6)
        self.xticks = self.xvalues
        self.xticklabels = [_("Unseen")] + range(0, 6)
        self.extra_hints["width"] = 0.5
        self.show_text_value = True
