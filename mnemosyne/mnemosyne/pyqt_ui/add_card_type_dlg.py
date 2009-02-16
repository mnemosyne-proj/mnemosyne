#
# add_card_type_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_add_card_type_dlg import Ui_AddCardTypeDlg

from mnemosyne.libmnemosyne.component_manager import card_types
from mnemosyne.libmnemosyne.component_manager import component_manager


class AddCardTypeDlg(QDialog, Ui_AddCardTypeDlg):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.card_types = []
        for card_type in card_types():
            if card_type.can_be_subclassed:
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
        card_type_name_safe = card_type_name.encode('utf8')
        C = type(card_type_name_safe, (parent_instance.__class__, ),
                 {'name': card_type_name,
                  'defined_through_gui': True,
                  'can_be_subclassed': False,
                  'id': parent_instance.id + "." + card_type_name})
        component_manager.register("card_type", C())       
        QDialog.accept(self)
