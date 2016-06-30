#
# add_tags_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.pyqt_ui.add_cards_dlg import AddEditCards
from mnemosyne.pyqt_ui.ui_add_tags_dlg import Ui_AddTagsDlg


class AddTagsDlg(QtWidgets.QDialog, Ui_AddTagsDlg, AddEditCards):

    def __init__(self, return_values, **kwds):
        super().__init__(**kwds)
        if parent is None:
            parent = self.main_widget()
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.return_values = return_values
        self.update_tags_combobox("")

    def accept(self):
        self.return_values["tag_names"] = [c.strip() for c in \
                     str(self.tags.currentText()).split(',')]
        return QtWidgets.QDialog.accept(self)

