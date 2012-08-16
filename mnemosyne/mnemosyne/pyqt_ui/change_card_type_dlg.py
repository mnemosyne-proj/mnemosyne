#
# change_card_type_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_change_card_type_dlg import Ui_ChangeCardTypeDlg


class ChangeCardTypeDlg(QtGui.QDialog, Ui_ChangeCardTypeDlg, Component):

    def __init__(self, component_manager, current_card_type, return_values,
                 parent=None):
        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.card_type_by_name = {}
        self.return_values = return_values
        for card_type in self.card_types():
            if card_type != current_card_type:
                self.card_type_by_name[_(card_type.name)] = card_type
                self.card_types_widget.addItem(_(card_type.name))

    def accept(self):
        card_type_name = unicode(self.card_types_widget.currentText())
        self.return_values["new_card_type"] = \
            self.card_type_by_name[card_type_name]
        return QtGui.QDialog.accept(self)
