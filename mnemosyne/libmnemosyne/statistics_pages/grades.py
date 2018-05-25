#
# grades.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage


class Grades(PlotStatisticsPage):

    name = _("Grades")

    ALL_CARDS = -1

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.variants = [(self.ALL_CARDS, _("All cards"))]
        self.tag_with_internal_id = {}
        for tag in self.database().tags():
            if tag.name == "__UNTAGGED__":
                tag.name = _("Untagged")
            self.tag_with_internal_id[tag._id] = tag
            self.variants.append((tag._id, tag.name))

    def prepare_statistics(self, variant):
        self.x = list(range(-1, 6))
        if variant == self.ALL_CARDS:
            self.y = [self.database().card_count_for_grade \
                (grade, active_only=False) for grade in self.x]
        else:
            self.y = [self.database().card_count_for_grade_and_tag \
                (grade, self.tag_with_internal_id[variant], active_only=False) \
                for grade in self.x]
