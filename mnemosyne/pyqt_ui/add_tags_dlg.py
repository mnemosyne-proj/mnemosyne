#
# add_tags_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.pyqt_ui.add_cards_dlg import AddEditCards
from mnemosyne.pyqt_ui.ui_add_tags_dlg import Ui_AddTagsDlg


class AddTagsDlg(QtWidgets.QDialog, AddEditCards, Ui_AddTagsDlg):

    def __init__(self, return_values, **kwds):
        
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.return_values = return_values
        self.update_tags_combobox("")

    def accept(self):
        self.return_values["tag_names"] = [c.strip() for c in \
                     self.tags.currentText().split(',')]
        return QtWidgets.QDialog.accept(self)

