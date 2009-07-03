#
# clone_card_type_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_clone_card_type_dlg import Ui_CloneCardTypeDlg


class CloneCardTypeDlg(QtGui.QDialog, Ui_CloneCardTypeDlg, Component):

    def __init__(self, parent, component_manager):
        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        for card_type in self.card_types():
            self.parent_type.addItem(card_type.name)

    def name_changed(self):
        if not self.name.text():
            self.OK_button.setEnabled(False)
        else:
            self.OK_button.setEnabled(True)

    def accept(self):
        parent_instance = self.card_types()[self.parent_type.currentIndex()]
        clone_name = unicode(self.name.text())
        clone = self.ui_controller_main().clone_card_type(\
            parent_instance, clone_name)
        if not clone:
            return
        QtGui.QDialog.accept(self)
