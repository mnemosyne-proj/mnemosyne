#
# activity_criterion.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class ActivityCriterion(Component):

    """Used to determine which cards are currently active, i.e. included in
    the review process.


    """

    criterion_type = ""

    def apply_to_card(self, card):

        """Set the card active or not depending on the criterion. Does not
        write to the database. Called after creating or updating cards, to
        see whether these cards should start out their life as active or not.

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
    
    def card_reviewed(self, card):
        pass
    
    def to_string(self):

        """Convert variables to a string for storage in the database. We don't
        use pickle here as that would make it difficult for non-Python programs
        to read the database.

        """
        
        raise NotImplementedError

    def from_string(self):
        raise NotImplementedError        


class CriterionApplier(Component):

    """Can be registered 'used_for' a certain ActivityCriterion to apply it in
    bulk to all the cards in the database. Is much faster than fetching each
    card from the database, calling ActivityCriterion.apply_to_card, and
    storing it back in the database.

    'active_or_in_view' is 'ACTIVE' or 'IN_VIEW', depending on whether the
    criterion needs to be applied to the review process, or just the temporary
    display of cards in the 'Browse cards' dialog.

    This code is not part of ActivityCriterion, because it is dependent on
    the database backend.

    """

    component_type = "criterion_applier"

    ACTIVE = 0
    IN_VIEW = 1

    def apply_to_database(self, active_or_in_view):
        raise NotImplementedError        
