#
# card_type_widget.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.ui_component import UiComponent


class CardTypeWidget(UiComponent):
    
    """'used_for' should be set to card type class that it corresponds to.
    If a card type has no dedicated card type widget, it is the responsibility
    of the GUI to provide a generic card type widget.

    """

    component_type = "card_type_widget"
    instantiate = Component.LATER

    def contains_data(self):
        raise NotImplementedError

    def get_data(self, check_for_required=True):

        """Get fact data from widget, optionally check for required fields.
        Should raise a ValueError if required fields are missing.

        """

        raise NotImplementedError
    
    def set_data(self, data):

        """Put fact data in the widget. Used e.g. when converting facts to
        different card types.


        """

        raise NotImplementedError

    def clear(self):

        """Empty the widget and prepare it for entry of the next card."""
        
        raise NotImplementedError

    
class GenericCardTypeWidget(CardTypeWidget):
    
    """A card type widget that can be used as fallback when no dedicated
    widget exists.

    """

    component_type = "generic_card_type_widget"
