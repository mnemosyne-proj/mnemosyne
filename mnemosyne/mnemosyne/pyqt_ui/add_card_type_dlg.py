#
# add_card_type_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_add_card_type_dlg import Ui_AddCardTypeDlg


class AddCardTypeDlg(QDialog, Ui_AddCardTypeDlg):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

    def accept(self):
        QDialog.accept()
