#
# manage_card_types_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_manage_card_types_dlg import Ui_ManageCardTypesDlg

from add_card_type_dlg import AddCardTypeDlg


class ManageCardTypesDlg(QDialog, Ui_ManageCardTypesDlg):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

    def add_card_type(self):
        dlg = AddCardTypeDlg(self)
        dlg.exec_()

    def help(self):
        message = _("Here, you can make copies of existing card types. This allows you to format the cards in this type independently from the original type. E.g. you could make a copy of 'Foreign word with pronunciation', call it 'Thai' and set a Thai fonts specifically for this card type without disturbing the other cards.")
        QMessageBox.information(self, _("Managing card types"), message, _("&OK"))
