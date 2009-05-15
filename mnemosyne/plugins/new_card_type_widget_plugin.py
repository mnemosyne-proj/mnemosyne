#
# new_card_type_widget_plugin.py <Peter.Bienstman@UGent.be>
#

# Colour the widget for the front to back card type red.
# Plugin version.

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
from mnemosyne.pyqt_ui.generic_card_type_widget import GenericCardTypeWdgt

# Don't forget to inherit from CardTypeWidget located in
# mnemosyne.libmnemosyne.ui_components.card_type_widget!
# (Here this is already fullfilled because GenericCardTypeWdgt itself inherits
# from CardTypeWidget)

class RedGenericCardTypeWdgt(GenericCardTypeWdgt):

    used_for = FrontToBack

    def __init__(self, prefill_data=None, parent=None):
        GenericCardTypeWdgt.__init__(self, FrontToBack(), prefill_data, parent)
        for edit_box in self.edit_boxes:
            p = QtGui.QPalette()
            p.setColor(QtGui.QPalette.Active, QtGui.QPalette.Base, \
                       QtGui.QColor("red"))
            edit_box.setPalette(p)

# Wrap it into a Plugin and then register the Plugin.

class RedPlugin(Plugin):
    name = "Red"
    description = "Red widget for front-to-back cards"
    components = [RedGenericCardTypeWdgt]

component_manager.register(RedPlugin())



