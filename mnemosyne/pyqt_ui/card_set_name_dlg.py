#
# card_set_name_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_component import UiComponent
from mnemosyne.pyqt_ui.ui_card_set_name_dlg import Ui_CardSetNameDlg


class CardSetNameDlg(QtWidgets.QDialog, UiComponent, Ui_CardSetNameDlg):

    def __init__(self, criterion, existing_names, **kwds):
        super().__init__(**kwds)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.setupUi(self)
        self.criterion = criterion
        self.set_name.addItem(criterion.name)
        if criterion.name == "":
            self.ok_button.setEnabled(False)
        for name in sorted(existing_names):
            self.set_name.addItem(name)

    def text_changed(self):
        if self.set_name.currentText():
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)

    def reject(self):
        return QtWidgets.QDialog.reject(self)

    def accept(self):
        self.criterion.name = self.set_name.currentText()
        return QtWidgets.QDialog.accept(self)

