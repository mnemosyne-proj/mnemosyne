#
# new_card_type_widget.py <Peter.Bienstman@UGent.be>
#

# Colour the widget for the front to back card type red. Version
# which does not go through the trouble of making a Plugin, i.e.
# it will always be active as soon as the program starts.

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
from mnemosyne.libmnemosyne.ui_components.card_type_widget \
     import CardTypeWidget
from mnemosyne.pyqt_ui.generic_card_type_widget import GenericCardTypeWdgt

# Don't forget to inherit from CardTypeWidget!

class RedGenericCardTypeWdgt(GenericCardTypeWdgt, CardTypeWidget):

    used_for = FrontToBack

    def __init__(self, prefill_data=None, parent=None):
        GenericCardTypeWdgt.__init__(self, FrontToBack(), prefill_data, parent)
        for edit_box in self.edit_boxes:
            p = QtGui.QPalette()
            p.setColor(QtGui.QPalette.Active, QtGui.QPalette.Base, \
                       QtGui.QColor("red"))
            edit_box.setPalette(p)

# Register the widget.

component_manager.register(RedGenericCardTypeWdgt)



    



