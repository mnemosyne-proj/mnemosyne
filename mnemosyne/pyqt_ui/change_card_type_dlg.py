#
# change_card_type_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_change_card_type_dlg import Ui_ChangeCardTypeDlg


class ChangeCardTypeDlg(QtWidgets.QDialog, Component, Ui_ChangeCardTypeDlg):

    def __init__(self, current_card_type, return_values, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.card_type_by_name = {}
        self.return_values = return_values
        for card_type in self.database().sorted_card_types():
            if card_type == current_card_type or card_type.hidden_from_UI:
                continue
            self.card_type_by_name[_(card_type.name)] = card_type
            self.card_types_widget.addItem(_(card_type.name))

    def accept(self):
        card_type_name = self.card_types_widget.currentText()
        self.return_values["new_card_type"] = \
            self.card_type_by_name[card_type_name]
        return QtWidgets.QDialog.accept(self)
