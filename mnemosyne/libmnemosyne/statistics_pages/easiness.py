#
# easiness.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.tag_tree import TagTree
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage


class Easiness(PlotStatisticsPage):

    name = _("Easiness")

    ALL_CARDS = -2
    ACTIVE_CARDS = -1

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.tag_tree = TagTree(self.component_manager, count_cards=False)
        self.nodes = self.tag_tree.nodes()
        self.variants = [(self.ALL_CARDS, _("All cards")),
                         (self.ACTIVE_CARDS, _("Active cards only"))]
        for index, node in enumerate(self.nodes):
            if node == "__UNTAGGED__":
                node = _("Untagged")
            self.variants.append((index, node))

    def prepare_statistics(self, variant):
        if variant == self.ALL_CARDS:
            self.data = self.database().easinesses(active_only=False)
        elif variant == self.ACTIVE_CARDS:
            self.data = self.database().easinesses(active_only=True)
        else:
            self.data = []
            for tag in self.tag_tree.tags_in_subtree(self.nodes[variant]):
                self.data.extend(self.database().easinesses_for_tag\
                                 (tag, active_only=False))

