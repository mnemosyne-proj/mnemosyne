#
# clone_card_type_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_clone_card_type_dlg import Ui_CloneCardTypeDlg
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component


class CloneCardTypeDlg(QDialog, Ui_CloneCardTypeDlg, Component):

    def __init__(self, parent, component_manager):
        Component.__init__(self, component_manager)
        QDialog.__init__(self, parent)
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
        try:
            parent_instance.clone(clone_name)
        except NameError:
            QMessageBox.critical(None, _("Mnemosyne"),
                                 _("This name is already in use."))
            return     
        QDialog.accept(self)
