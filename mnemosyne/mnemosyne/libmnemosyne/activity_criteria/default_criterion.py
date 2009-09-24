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

    def data_to_string(self):
        return repr(([(card_type_fact_view[0].id, card_type_fact_view[1].id) \
                      for card_type_fact_view in self.deactivated_card_type_fact_views],
                     [tag.name for tag in self.required_tags],
                     [tag.name for tag in self.forbidden_tags]))
    
    def data_from_string(self, data):
        data = eval(data)
        self.deactivated_card_type_fact_views = set()
        for card_type_id_fact_view_id in data[0]:
            card_type_id, fact_view_id = card_type_id_fact_view_id
            card_type = self.card_type_by_id(card_type_id)
            for fact_view in card_type.fact_views:
                if fact_view.id == fact_view_id:
                    self.deactivated_card_type_fact_views.add(\
                        (card_type, fact_view))
                    break
        db = self.database()
        self.required_tags = \
            set([db.get_or_create_tag_with_name(name) for name in data[1]])
        self.forbidden_tags = \
            set([db.get_or_create_tag_with_name(name) for name in data[2]])
