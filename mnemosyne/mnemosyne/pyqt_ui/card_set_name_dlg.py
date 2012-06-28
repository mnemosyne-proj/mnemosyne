#
# card_set_name_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_component import UiComponent
from mnemosyne.pyqt_ui.ui_card_set_name_dlg import Ui_CardSetNameDlg


class CardSetNameDlg(QtGui.QDialog, Ui_CardSetNameDlg, UiComponent):

    def __init__(self, component_manager, criterion, existing_names, parent):
        UiComponent.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.setupUi(self)
        self.criterion = criterion
        self.set_name.addItem("")
        for name in sorted(existing_names):
            self.set_name.addItem(name)
        self.ok_button.setEnabled(False)

    def text_changed(self):
        if self.set_name.currentText():
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)

    def reject(self):
        self.criterion.name = ""
        return QtGui.QDialog.reject(self)

    def accept(self):
        self.criterion.name = unicode(self.set_name.currentText())
        return QtGui.QDialog.accept(self)

