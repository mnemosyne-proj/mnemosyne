#
# clone_card_type_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_clone_card_type_dlg import Ui_CloneCardTypeDlg

from mnemosyne.libmnemosyne.component_manager import card_types


class CloneCardTypeDlg(QDialog, Ui_CloneCardTypeDlg):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.card_types = []
        for card_type in card_types():
            if not card_type.is_clone:
                self.parent_type.addItem(card_type.name)
                self.card_types.append(card_type)

    def name_changed(self):
        if not self.name.text():
            self.OK_button.setEnabled(False)
        else:
            self.OK_button.setEnabled(True)

    def accept(self):
        parent_instance = self.card_types[self.parent_type.currentIndex()]
        card_type_name = unicode(self.name.text())
        try:
            parent_instance.clone(card_type_name)
        except NameError:
            QMessageBox.critical(None, _("Mnemosyne"),
                                 _("This name is already in use."))
            return     
        QDialog.accept(self)
