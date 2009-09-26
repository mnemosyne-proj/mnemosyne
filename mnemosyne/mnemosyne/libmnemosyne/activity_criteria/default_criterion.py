#
# default_criterion.py - <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.activity_criterion import ActivityCriterion


class DefaultCriterion(ActivityCriterion):

    criterion_type = "default"

    def __init__(self, component_manager):
        ActivityCriterion.__init__(self, component_manager)
        self.name = ""
        # (card_type.id, fact_view.id):
        self.deactivated_card_type_fact_view_ids = set()
        self.required_tag__ids = set()
        self.forbidden_tag__ids = set()

    def apply_to_card(self, card):
        # TODO: update
        card.active = False
        if card.tags.intersection(self.required_tags):
            card.active = True
        if (card.fact.card_type, card.fact_view) in \
           self.deactivated_card_type_fact_views:
            card.active = False
        if card.tags.intersection(self.forbidden_tags):
            card.active = False
    
    def tag_created(self, tag):
        self.required_tag__ids.add(tag._id)

    def tag_deleted(self, tag):
        self.required_tag__idss.discard(tag._id)
        self.forbidden_tag__ids.discard(tag._id)

    def card_type_created(self, card_type):
        pass

    def card_type_deleted(self, card_type):
        pass

    def data_to_string(self):
        return repr((self.deactivated_card_type_fact_view_ids,
                     self.required_tag__ids,
                     self.forbidden_tag__ids))
    
    def data_from_string(self, data):
        data = eval(data)
        self.deactivated_card_type_fact_view_ids = data[0]
        self.required_tag__ids = data[1]
        self.forbidden_tag__ids = data[2]
