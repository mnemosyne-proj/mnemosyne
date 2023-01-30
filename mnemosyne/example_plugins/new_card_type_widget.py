#
# new_card_type_widget.py <Peter.Bienstman@gmail.com>
#

# Colour the widget for the front to back card type red.

from PyQt6 import QtGui

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
from mnemosyne.pyqt_ui.card_type_wdgt_generic import GenericCardTypeWdgt


# Don't forget to inherit from CardTypeWidget located in
# mnemosyne.libmnemosyne.ui_components.card_type_widget!
# (Here this is already fullfilled because GenericCardTypeWdgt itself inherits
# from CardTypeWidget.)
# We inherit from GenericCardTypeWdgt purely for implementation reasons.
# What we are building here is a CardTypeWidget (specific for the FrontToBack
# card type), not a GenericCardTypeWidget, so we need to respecify the
# component_type.

class RedCardTypeWdgt(GenericCardTypeWdgt):

    component_type = "card_type_widget"
    used_for = FrontToBack

    def __init__(self, **kwds):
        super().__init__(**kwds)
        for edit_box in self.edit_boxes:
            p = QtGui.QPalette()
            p.setColor(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base, \
                       QtGui.QColor("red"))
            edit_box.setPalette(p)


# Wrap it into a Plugin and then register the Plugin.

class RedPlugin(Plugin):
    
    name = "Red"
    description = "Red widget for front-to-back cards"
    components = [RedCardTypeWdgt]
    supported_API_level = 3

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(RedPlugin)




