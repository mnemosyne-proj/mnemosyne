#
# easiness.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage


class Easiness(PlotStatisticsPage):

    name = _("Easiness")
    
    ALL_CARDS = -1

    def __init__(self, component_manager):
        PlotStatisticsPage.__init__(self, component_manager)
        self.variants = [(self.ALL_CARDS, _("All cards"))]
        for _id, name in self.database().tags__id_and_name():
            self.variants.append((_id, name))
        
    def prepare_statistics(self, variant):                
        if variant == self.ALL_CARDS:
            self.data = self.database().easinesses()
        else:
            self.data = self.database().easinesses_for__tag_id(variant)
            