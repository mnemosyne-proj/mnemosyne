#
# grades.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.tag_tree import TagTree
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage


class Grades(PlotStatisticsPage):

    name = _("Grades")

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
        self.x = list(range(-1, 6))
        if variant == self.ALL_CARDS:
            self.y = [self.database().card_count_for_grade \
                (grade, active_only=False) for grade in self.x]
        elif variant == self.ACTIVE_CARDS:
            self.y = [self.database().card_count_for_grade \
                (grade, active_only=True) for grade in self.x]
        else:
            self.y = []
            for grade in self.x:
                self.y.append(0)
                for tag in self.tag_tree.tags_in_subtree(self.nodes[variant]):
                    self.y[-1] += self.database().card_count_for_grade_and_tag \
                        (grade, tag, active_only=False)
