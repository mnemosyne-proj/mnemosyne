#
# default_criterion.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.activity_criterion import ActivityCriterion


class DefaultCriterion(ActivityCriterion):

    criterion_type = "Default"
    
    def __init__(self, component_manager, id=None):
        ActivityCriterion.__init__(self, component_manager, id)
        # (card_type.id, fact_view.id):
        self.deactivated_card_type_fact_view_ids = set()
        # We work with _ids instead of ids for speed.
        self.active_tag__ids = set()
        self.forbidden_tag__ids = set()

    def apply_to_card(self, card):
        card.active = False
        for tag in card.tags:
            if tag._id in self.active_tag__ids:
                card.active = True
                break
        if (card.card_type.id, card.fact_view.id) in \
           self.deactivated_card_type_fact_view_ids:
            card.active = False
        for tag in card.tags:
            if tag._id in self.forbidden_tag__ids:
                card.active = False
                break
    
    def tag_created(self, tag):
        self.active_tag__ids.add(tag._id)

    def tag_deleted(self, tag):
        self.active_tag__ids.discard(tag._id)
        self.forbidden_tag__ids.discard(tag._id)

    def card_type_created(self, card_type):
        pass

    def card_type_deleted(self, card_type):
        for fact_view in card_type.fact_views:
            self.deactivated_card_type_fact_view_ids.discard(\
                (card_type.id, fact_view.id))

    def data_to_string(self):
        return repr((self.deactivated_card_type_fact_view_ids,
                     self.active_tag__ids,
                     self.forbidden_tag__ids))
    
    def set_data_from_string(self, data_string):
        data = eval(data_string)
        self.deactivated_card_type_fact_view_ids = data[0]
        self.active_tag__ids = data[1]
        self.forbidden_tag__ids = data[2]

    # To send the activity criteria across, we need to convert from _ids
    # ids first.
    
    def data_to_sync_string(self):
        active_tag_ids = set()
        for tag__id in self.active_tag__ids:
            tag = self.database().tag(tag__id, id_is_internal=True)
            active_tag_ids.add(tag.id)
        forbidden_tag_ids = set()
        for tag__id in self.forbidden_tag__ids:
            tag = self.database().tag(tag__id, id_is_internal=True)
            forbidden_tag_ids.add(tag.id)
        return repr((self.deactivated_card_type_fact_view_ids,
                     active_tag_ids, forbidden_tag_ids))

    def set_data_from_sync_string(self, data_string):
        data = eval(data_string)
        self.deactivated_card_type_fact_view_ids = data[0]
        active_tag_ids = data[1]
        forbidden_tag_ids = data[2]
        self.active_tag__ids = set()
        for tag_id in active_tag_ids:
            tag = self.database().tag(tag_id, id_is_internal=False)
            self.active_tag__ids.add(tag._id)        
        self.forbidden_tag__ids = set()
        for tag_id in forbidden_tag_ids:
            tag = self.database().tag(tag_id, id_is_internal=False)
            self.forbidden_tag__ids.add(tag._id)        
