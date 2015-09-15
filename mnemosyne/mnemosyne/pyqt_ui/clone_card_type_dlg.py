#
# clone_card_type_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_clone_card_type_dlg import Ui_CloneCardTypeDlg


class CloneCardTypeDlg(QtGui.QDialog, Ui_CloneCardTypeDlg, Component):

    def __init__(self, parent, component_manager):
        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.sorted_card_types = self.database().sorted_card_types()
        for card_type in self.sorted_card_types:
            self.parent_type.addItem(_(card_type.name))

    def name_changed(self):
        if not self.name.text():
            self.OK_button.setEnabled(False)
        else:
            self.OK_button.setEnabled(True)

    def accept(self):
        parent_instance = self.sorted_card_types[self.parent_type.currentIndex()]
        clone_name = unicode(self.name.text())
        clone = self.controller().clone_card_type(\
            parent_instance, clone_name)
        if not clone:
            return
        QtGui.QDialog.accept(self)
