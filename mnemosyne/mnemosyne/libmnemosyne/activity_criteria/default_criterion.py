#
# default_criterion.py - <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.activity_criterion import ActivityCriterion


class DefaultCriterion(ActivityCriterion):

    criterion_type = "default"

    def apply_to_card(self, card):
        pass

    def to_string(self):
        pass
    
    def from_string(self):
        pass
