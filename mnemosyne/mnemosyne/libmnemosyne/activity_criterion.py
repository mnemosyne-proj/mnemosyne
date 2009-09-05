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

        """
        
        raise NotImplementedError

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

    This code is not part of ActivityCriterion, because it is dependent on
    the database backend.

    """

    component_type = "criterion_applier"

    def apply_to_database(self):
        raise NotImplementedError        
