#
# manage_card_types_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.pyqt_ui.clone_card_type_dlg import CloneCardTypeDlg
from mnemosyne.pyqt_ui.ui_manage_card_types_dlg import Ui_ManageCardTypesDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ManageCardTypesDialog


class ManageCardTypesDlg(QtWidgets.QDialog, ManageCardTypesDialog,
                         Ui_ManageCardTypesDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.update()

    def activate(self):
        ManageCardTypesDialog.activate(self)
        self.exec_()

    def update(self):
        self.cloned_card_types.clear()
        self.items = []
        self.card_type_with_item = []
        for card_type in self.database().sorted_card_types():
            if self.database().is_user_card_type(card_type):
                name = "%s (%s)" % (_(card_type.name),
                                    _(card_type.__class__.__bases__[0].name))
                item = QtWidgets.QListWidgetItem(name)
                self.cloned_card_types.addItem(item)
                # Since node_item seems mutable, we cannot use a dict.
                self.items.append(item)
                self.card_type_with_item.append(card_type)
        if self.cloned_card_types.count() == 0:
            self.rename_button.setEnabled(False)
            self.delete_button.setEnabled(False)
        else:
            self.rename_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.cloned_card_types.item(0).setSelected(True)

    def clone_card_type(self):
        if not self.config()["clone_help_shown"]:
            self.main_widget().show_information(\
_("Here, you can make clones of existing card types. This allows you to format cards in this type independently from cards in the original type. E.g. you can make a clone of 'Vocabulary', call it 'Thai' and set a Thai font specifically for this card type without disturbing your other cards."))
            self.config()["clone_help_shown"] = True
        dlg = CloneCardTypeDlg(parent=self, component_manager=self.component_manager)
        dlg.exec_()
        self.update()

    def delete_card_type(self):
        if len(self.cloned_card_types.selectedItems()) == 0:
            return
        answer = self.main_widget().show_question\
            (_("Delete this card type?"), _("&OK"), _("&Cancel"), "")
        if answer == 1: # Cancel.
            return
        selected_item = self.cloned_card_types.selectedItems()[0]
        for i in range(len(self.items)):
            if selected_item == self.items[i]:
                card_type = self.card_type_with_item[i]
                self.controller().delete_card_type(card_type)
                self.update()
                return

    def rename_card_type(self):
        if len(self.cloned_card_types.selectedItems()) == 0:
            return

        from mnemosyne.pyqt_ui.ui_rename_card_type_dlg \
            import Ui_RenameCardTypeDlg

        class RenameDlg(QtWidgets.QDialog, Ui_RenameCardTypeDlg):
            def __init__(self, old_card_type_name):
                super().__init__()
                self.setupUi(self)
                self.card_type_name.setText(old_card_type_name)

        selected_item = self.cloned_card_types.selectedItems()[0]
        for i in range(len(self.items)):
            if selected_item == self.items[i]:
                card_type = self.card_type_with_item[i]
                dlg = RenameDlg(card_type.name)
                if dlg.exec_() == QtWidgets.QDialog.Accepted:
                    new_name = dlg.card_type_name.text()
                    self.controller().rename_card_type(card_type, new_name)
                self.update()
                return
