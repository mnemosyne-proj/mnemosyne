#
# activity_criterion.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class ActivityCriterion(Component):

    """Used to determine which cards are currently active, i.e. included in
    the review process.

    The available Criteria are stored as classes in the component_manager.

    The actual instances together with their data are stored in the database.

    """

    component_type = "activity_criterion"   
    criterion_type = ""
    instantiate = Component.LATER
    
    def __init__(self, component_manager, id=None):
        Component.__init__(self, component_manager)
        self.name = ""
        if id is None:
            import uuid
            id = str(uuid.uuid4())
        self.id = id
        self._id = None
            
    def apply_to_card(self, card):

        """Set the card active or not depending on the criterion. Does not
        write to the database. Called after creating or updating cards, to
        see whether these cards should start out their life as active or not.

        Also called after reviewing a card.

        The tag and card type creation and deletion function are callbacks
        called by the rest of libmnemosyne when these objects get created or
        destroyed, such that ActivityCriteria can update their status if
        needed.

        """
        
        raise NotImplementedError

    def tag_created(self, tag):
        pass

    def tag_deleted(self, tag):
        pass

    def card_type_created(self, card_type):
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

    """Can be registered 'used_for' a certain ActivityCriterion to apply it in
    bulk to all the cards in the database. Is much faster than fetching each
    card from the database, calling ActivityCriterion.apply_to_card, and
    storing it back in the database.

    This code is not part of ActivityCriterion, because it is dependent on
    the database backend.

    """

    component_type = "criterion_applier"

    def apply_to_database(self, criterion):
        raise NotImplementedError        
