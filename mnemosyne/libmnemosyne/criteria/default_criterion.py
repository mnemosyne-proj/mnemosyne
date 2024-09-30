#
# default_criterion.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.criterion import Criterion


class DefaultCriterion(Criterion):

    criterion_type = "default"

    def __init__(self, component_manager, id=None):
        Criterion.__init__(self, component_manager, id)
        # (card_type.id, fact_view.id):
        self.deactivated_card_type_fact_view_ids = set()
        # We work with _ids instead of ids for speed.
        self._tag_ids_active = set()
        self._tag_ids_forbidden = set()

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.deactivated_card_type_fact_view_ids == \
                other.deactivated_card_type_fact_view_ids \
            and self._tag_ids_active == other._tag_ids_active \
            and self._tag_ids_forbidden == other._tag_ids_forbidden

    def is_empty(self):
        # Check card types.
        counter = 0
        for card_type in self.card_types():
            counter += len(card_type.fact_views)
        if len(self.deactivated_card_type_fact_view_ids) == counter:
            return True
        # Active tags.
        elif len(self._tag_ids_active) == 0:
            return True
        # Forbidden tags.
        elif len(self.database().tags()) == len(self._tag_ids_forbidden):
            return True
        else:
            return False

    def apply_to_card(self, card):
        card.active = False
        for tag in card.tags:
            if tag._id in self._tag_ids_active:
                card.active = True
                break
        if (card.card_type.id, card.fact_view.id) in \
           self.deactivated_card_type_fact_view_ids:
            card.active = False
        for tag in card.tags:
            if tag._id in self._tag_ids_forbidden:
                card.active = False
                break

    def active_tag_added(self, tag):
        self._tag_ids_active.add(tag._id)

    def deactivated_tag_added(self, tag):
        # Since the UI only supports criteria which either have active tags or
        # forbidden tags, but not both, we need to maintain that situation when
        # adding tags.
        if len(self._tag_ids_forbidden) != 0:
            self._tag_ids_forbidden.add(tag._id)
        else:
            pass

    def is_tag_active(self, tag):
        return (tag._id in self._tag_ids_active)
    
    def tag_deleted(self, tag):
        self._tag_ids_active.discard(tag._id)
        self._tag_ids_forbidden.discard(tag._id)

    def active_card_type_added(self, card_type):
        pass

    def deactivated_card_type_added(self, card_type):
        for fact_view in card_type.fact_views:
            self.deactivated_card_type_fact_view_ids.add(\
                (card_type.id, fact_view.id))

    def card_type_deleted(self, card_type):
        for fact_view in card_type.fact_views:
            self.deactivated_card_type_fact_view_ids.discard(\
                (card_type.id, fact_view.id))

    def data_to_string(self):
        return repr((self.deactivated_card_type_fact_view_ids,
                     self._tag_ids_active,
                     self._tag_ids_forbidden))

    def set_data_from_string(self, data_string):
        data = eval(data_string)
        self.deactivated_card_type_fact_view_ids = data[0]
        self._tag_ids_active = data[1]
        self._tag_ids_forbidden = data[2]

    # To send the criteria across, we need to convert from _ids ids first.

    def data_to_sync_string(self):
        active_tag_ids = set()
        for _tag_id in self._tag_ids_active:
            tag = self.database().tag(_tag_id, is_id_internal=True)
            active_tag_ids.add(tag.id)
        forbidden_tag_ids = set()
        for _tag_id in self._tag_ids_forbidden:
            tag = self.database().tag(_tag_id, is_id_internal=True)
            forbidden_tag_ids.add(tag.id)
        return repr((self.deactivated_card_type_fact_view_ids,
                     active_tag_ids, forbidden_tag_ids))

    def set_data_from_sync_string(self, data_string):
        data = eval(data_string)
        self.deactivated_card_type_fact_view_ids = data[0]
        active_tag_ids = data[1]
        forbidden_tag_ids = data[2]
        self._tag_ids_active = set()
        for tag_id in active_tag_ids:
            tag = self.database().tag(tag_id, is_id_internal=False)
            self._tag_ids_active.add(tag._id)
        self._tag_ids_forbidden = set()
        for tag_id in forbidden_tag_ids:
            tag = self.database().tag(tag_id, is_id_internal=False)
            self._tag_ids_forbidden.add(tag._id)
