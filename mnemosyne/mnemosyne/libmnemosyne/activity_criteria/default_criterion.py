#
# default_criterion.py - <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.activity_criterion import ActivityCriterion


class DefaultCriterion(ActivityCriterion):

    criterion_type = "default"

    def __init__(self, component_manager):
        ActivityCriterion.__init__(self, component_manager)
        self.name = ""
        self.deactivated_card_type_fact_views = set() # (card_type, fact_view)
        self.required_tags = set()
        self.forbidden_tags = set()

    def apply_to_card(self, card):
        card.active = False
        if card.tags.intersection(self.required_tags):
            card.active = True
        if (card.fact.card_type, card.fact_view) in \
           self.deactivated_card_type_fact_views:
            card.active = False
        if card.tags.intersection(self.forbidden_tags):
            card.active = False
    
    def tag_created(self, tag):
        self.required_tags.add(tag)

    def tag_deleted(self, tag):
        self.required_tags.discard(tag)
        self.forbidden_tags.discard(tag)

    def card_type_created(self, card_type):
        pass

    def card_type_deleted(self, card_type):
        pass

    def card_reviewed(self, card):
        pass

    def to_string(self):
        pass
    
    def from_string(self):
        pass
