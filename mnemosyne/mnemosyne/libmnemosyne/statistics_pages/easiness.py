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
        self.tag_with_internal_id = {}
        for tag in self.database().tags():
            if tag.name == "__UNTAGGED__":
                tag.name = _("Untagged")
            self.tag_with_internal_id[tag._id] = tag
            self.variants.append((tag._id, tag.name))
        
    def prepare_statistics(self, variant):                
        if variant == self.ALL_CARDS:
            self.data = self.database().easinesses(active_only=True)
        else:
            self.data = self.database().easinesses_for_tag\
                (self.tag_with_internal_id[variant], active_only=True)
            