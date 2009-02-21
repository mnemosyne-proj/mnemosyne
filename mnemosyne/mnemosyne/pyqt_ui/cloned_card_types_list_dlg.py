#
# cloned_card_types_list_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from clone_card_type_dlg import CloneCardTypeDlg

from ui_cloned_card_types_list_dlg import Ui_ClonedCardTypesListDlg

from mnemosyne.libmnemosyne.component_manager import card_types


class ClonedCardTypesListDlg(QDialog, Ui_ClonedCardTypesListDlg):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.update()

    def update(self):
        self.cloned_card_types.clear()
        for card_type in card_types():
            if card_type.is_clone:
                name = "%s (%s)" % (card_type.name,
                                    card_type.__class__.__bases__[0].name)
                self.cloned_card_types.addItem(QListWidgetItem(name))

    def clone_card_type(self):
        dlg = CloneCardTypeDlg(self)
        dlg.exec_()
        self.update()

    def help(self):
        message = _("Here, you can make clones of existing card types. This allows you to format the cards in this type independently from the original type. E.g. you could make a clone of 'Foreign word with pronunciation', call it 'Thai' and set a Thai fonts specifically for this card type without disturbing the other cards.")
        QMessageBox.information(self, _("Cloning card types"), message, _("&OK"))
