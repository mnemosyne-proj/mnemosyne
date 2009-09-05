#
# default_criterion.py - <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.activity_criterion import ActivityCriterion


class DefaultCriterion(ActivityCriterion):

    criterion_type = "default"

    def __init__(self):
        self.name = ""
        self.deactivated_fact_views = []
        self.required_tags = []
        self.forbidden_tags = []

    def apply_to_card(self, card):
        pass
    
    def tag_created(self, tag):
        pass

    def tag_deleted(self, tag):
        pass

    def card_type_created(self, card_type):
        pass

    def card_type_deleted(self, card_type):
        pass

    def to_string(self):
        pass
    
    def from_string(self):
        pass
