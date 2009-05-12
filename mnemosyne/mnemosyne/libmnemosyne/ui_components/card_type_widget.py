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
    
