#
# cloned_card_types_list_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.clone_card_type_dlg import CloneCardTypeDlg
from mnemosyne.pyqt_ui.ui_cloned_card_types_list_dlg import \
     Ui_ClonedCardTypesListDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ManageCardTypesDialog

class ClonedCardTypesListDlg(QtGui.QDialog, Ui_ClonedCardTypesListDlg,
                             ManageCardTypesDialog):

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.update()

    def activate(self):
        self.exec_()

    def update(self):
        self.cloned_card_types.clear()
        for card_type in self.card_types():
            if card_type.__class__.__bases__[0] != CardType:
                name = "%s (%s)" % (card_type.name,
                                    card_type.__class__.__bases__[0].name)
                self.cloned_card_types.addItem(QtGui.QListWidgetItem(name))

    def clone_card_type(self):
        dlg = CloneCardTypeDlg(self, self.component_manager)
        dlg.exec_()
        self.update()

    def help(self):
        message = _("Here, you can make clones of existing card types. This allows you to format the cards in this type independently from the original type. E.g. you could make a clone of 'Foreign word with pronunciation', call it 'Thai' and set a Thai fonts specifically for this card type without disturbing the other cards.")
        QtGui.QMessageBox.information(self, _("Cloning card types"), message, _("&OK"))
