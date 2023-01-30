#
# criterion.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.utils import rand_uuid
from mnemosyne.libmnemosyne.component import Component


class Criterion(Component):

    """Used to select a subset of cards, e.g. which cards are currently
    active, i.e. included in the review process.

    The available criteria are stored as classes in the component_manager,
    the actual instances together with their data are stored in the database.

    """

    component_type = "criterion"
    criterion_type = ""
    instantiate = Component.LATER

    def __init__(self, component_manager, id=None):
        Component.__init__(self, component_manager)
        self.name = ""
        if id is None:
            id = rand_uuid()
        self.id = id
        self._id = None

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_empty(self):

        """Used to prevent people from creating a criterion which can never
        contain any cards (e.g. disabling all card types).

        """

        return False

    def apply_to_card(self, card):

        """Set the card active or not depending on the criterion. Does not
        write to the database. Called e.g. after creating, updating or
        reviewing cards, to see whether these cards should start out their
        life as active or not.

        The tag and card type creation and deletion functions are callbacks
        called by the rest of libmnemosyne when these objects get created or
        destroyed, such that Criteria can update their status if needed.

        """

        raise NotImplementedError

    def active_tag_added(self, tag):
        pass

    def deactivated_tag_added(self, tag):
        pass

    def is_tag_active(self, tag):
        pass
    
    def tag_deleted(self, tag):
        pass

    def active_card_type_added(self, card_type):
        pass

    def deactivated_card_type_added(self, card_type):
        pass

    def card_type_deleted(self, card_type):
        pass

    def data_to_string(self):

        """Convert variables to a string for storage in the database. We don't
        use pickle here as that would make it difficult for non-Python programs
        to read the database.

        """

        raise NotImplementedError

    def set_data_from_string(self, data_string):
        raise NotImplementedError

    def data_to_sync_string(self):

        """Convert variables to a string for sending across during syncing.
        Could be different from 'data_to_string', as it should use ids instead
        of _ids."""

        raise NotImplementedError

    def set_data_from_sync_string(self, data_string):
        raise NotImplementedError


class CriterionApplier(Component):

    """Can be registered 'used_for' a certain Criterion to apply it in bulk to
    all the cards in the database. Is much faster than fetching each card from
    the database, calling Criterion.apply_to_card, and storing it back in the
    database.

    This code is not part of Criterion, because it is dependent on the database
    backend.

    """

    component_type = "criterion_applier"

    def apply_to_database(self, criterion):
        raise NotImplementedError

