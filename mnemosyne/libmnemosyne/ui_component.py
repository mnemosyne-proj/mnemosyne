#
# ui_component.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component


class UiComponent(Component):

    """Apart from the main widget, UI components are instantiated late for
    efficiency reasons.

    """

    component_type = "ui_component"

    instantiate = Component.LATER

