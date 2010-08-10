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
        for _id, name in self.database().tags__id_and_name():
            self.variants.append((_id, name))
                
    def prepare_statistics(self, variant):
        self.x = range(-1, 6)
        if variant == self.ALL_CARDS:
            self.y = [self.database().card_count_for_grade\
                      (grade) for grade in self.x]
        else:
            self.y = [self.database().card_count_for_grade_and__tag_id\
                      (grade, variant) for grade in self.x]
            
                              
