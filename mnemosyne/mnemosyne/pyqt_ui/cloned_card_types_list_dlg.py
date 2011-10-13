#
# cloned_card_types_list_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

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
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.update()

    def activate(self):
        if not self.config()["clone_help_shown"]:
            self.main_widget().show_information(\
                _("Here, you can make clones of existing card types. This allows you to format cards in this type independently from cards in the original type. E.g. you can make a clone of 'Vocabulary', call it 'Thai' and set a Thai font specifically for this card type without disturbing your other cards."))
            self.config()["clone_help_shown"] = True
        self.retranslateUi(self)
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
        
