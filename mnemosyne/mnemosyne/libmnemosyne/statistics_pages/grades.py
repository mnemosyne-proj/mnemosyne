#
# grades.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage


class Grades(PlotStatisticsPage):

    name = _("Grades")
    
    ALL_CARDS = -1

    def __init__(self, component_manager):
        PlotStatisticsPage.__init__(self, component_manager)
        self.variants = [(self.ALL_CARDS, _("All cards"))]
        for _id, name in self.database().get_tags__id_and_name():
            self.variants.append((_id, name))
                
    def prepare_statistics(self, variant):
        self.x = range(-1, 6)
        self.y = [] # Don't forget to reset this after variant change.
        for grade in self.x:
            if variant == self.ALL_CARDS:
                self.y.append(self.database().\
                    card_count_for_grade(grade))
            else:
                self.y.append(self.database().\
                    card_count_for_grade_and__tag_id(grade, variant))
                              

